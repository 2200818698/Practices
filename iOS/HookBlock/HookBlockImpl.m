//
//  HookBlockImpl.m
//  DIDI
//
//  Created by sljr-姜毅 on 16/06/2018.
//  Copyright © 2018 HHH.DH.UR. All rights reserved.
//

#import "HookBlockImpl.h"
#import "ffi.h"
#import <CoreGraphics/CoreGraphics.h>
#import <objc/runtime.h>

static struct _DDBlock *originBlock;
static struct _DDBlock *replaceBlock;
static void *originInvoke;
static NSUInteger numberOfArguments;
static ffi_cif _cif;
static ffi_closure *_closure;

enum {
    BLOCK_HAS_COPY_DISPOSE =  (1 << 25),
    BLOCK_HAS_CTOR =          (1 << 26), // helpers have C++ code
    BLOCK_IS_GLOBAL =         (1 << 28),
    BLOCK_HAS_STRET =         (1 << 29), // IFF BLOCK_HAS_SIGNATURE
    BLOCK_HAS_SIGNATURE =     (1 << 30),
};

struct _DDBlockDescriptor {
    unsigned long reserved;
    unsigned long size;
    void *rest[1]; //enum
};

struct _DDBlock {
    void *isa;
    int flags;
    int reserved;
    void *invoke;//函数指针
    struct _DDBlockDescriptor *descriptor;//block 描述
};

typedef struct Argument{
    void *_Nullable *_Null_unspecified args;
    void *retValue;
    struct _DDBlock oBlock;
    struct _DDBlock rBlock;
}Argument;

static const char *DDBlockTypeEncodeString(id blockObj)
{
    struct _DDBlock *block = (__bridge void *)blockObj;
    struct _DDBlockDescriptor *descriptor = block->descriptor;
    
    assert(block->flags & BLOCK_HAS_SIGNATURE);
    
    int index = 0;
    if(block->flags & BLOCK_HAS_COPY_DISPOSE)
        index += 2;
    
    return descriptor->rest[index];
}

static const char *DDSizeAndAlignment(const char *str, NSUInteger *sizep, NSUInteger *alignp, long *len)
{
    const char *out = NSGetSizeAndAlignment(str, sizep, alignp);
    if(len)
        *len = out - str;
    while(isdigit(*out))
        out++;
    return out;
}

void *_allocate(size_t howmuch)
{
    NSMutableData *data = [NSMutableData dataWithLength:howmuch];
    return [data mutableBytes];
}

ffi_type *_ffiArgForEncode(const char *str)
{
#define SINT(type) do { \
if(str[0] == @encode(type)[0]) \
{ \
if(sizeof(type) == 1) \
return &ffi_type_sint8; \
else if(sizeof(type) == 2) \
return &ffi_type_sint16; \
else if(sizeof(type) == 4) \
return &ffi_type_sint32; \
else if(sizeof(type) == 8) \
return &ffi_type_sint64; \
else \
{ \
NSLog(@"Unknown size for type %s", #type); \
abort(); \
} \
} \
} while(0)
    
#define UINT(type) do { \
if(str[0] == @encode(type)[0]) \
{ \
if(sizeof(type) == 1) \
return &ffi_type_uint8; \
else if(sizeof(type) == 2) \
return &ffi_type_uint16; \
else if(sizeof(type) == 4) \
return &ffi_type_uint32; \
else if(sizeof(type) == 8) \
return &ffi_type_uint64; \
else \
{ \
NSLog(@"Unknown size for type %s", #type); \
abort(); \
} \
} \
} while(0)
    
#define INT(type) do { \
SINT(type); \
UINT(unsigned type); \
} while(0)
    
#define COND(type, name) do { \
if(str[0] == @encode(type)[0]) \
return &ffi_type_ ## name; \
} while(0)
    
#define PTR(type) COND(type, pointer)
    
#define STRUCT(structType, ...) do { \
if(strncmp(str, @encode(structType), strlen(@encode(structType))) == 0) \
{ \
ffi_type *elementsLocal[] = { __VA_ARGS__, NULL }; \
ffi_type **elements = _allocate(sizeof(elementsLocal)); \
memcpy(elements, elementsLocal, sizeof(elementsLocal)); \
\
ffi_type *structType = _allocate(sizeof(*structType)); \
structType->type = FFI_TYPE_STRUCT; \
structType->elements = elements; \
return structType; \
} \
} while(0)
    
    SINT(_Bool);
    SINT(signed char);
    UINT(unsigned char);
    INT(short);
    INT(int);
    INT(long);
    INT(long long);
    
    PTR(id);
    PTR(Class);
    PTR(SEL);
    PTR(void *);
    PTR(char *);
    PTR(void (*)(void));
    
    COND(float, float);
    COND(double, double);
    
    COND(void, void);
    
    ffi_type *CGFloatFFI = sizeof(CGFloat) == sizeof(float) ? &ffi_type_float : &ffi_type_double;
    STRUCT(CGRect, CGFloatFFI, CGFloatFFI, CGFloatFFI, CGFloatFFI);
    STRUCT(CGPoint, CGFloatFFI, CGFloatFFI);
    STRUCT(CGSize, CGFloatFFI, CGFloatFFI);
    
#if !TARGET_OS_IPHONE
    STRUCT(NSRect, CGFloatFFI, CGFloatFFI, CGFloatFFI, CGFloatFFI);
    STRUCT(NSPoint, CGFloatFFI, CGFloatFFI);
    STRUCT(NSSize, CGFloatFFI, CGFloatFFI);
#endif
    
    NSLog(@"Unknown encode string %s", str);
    abort();
}

static int DDArgCount(const char *str)
{
    int argcount = -1; // return type is the first one
    while(str && *str)
    {
        str = DDSizeAndAlignment(str, NULL, NULL, NULL);
        argcount++;
    }
    return argcount;
}

ffi_type **_argsWithEncodeString(const char *str, int *outCount)
{
    //这个参数个数应该从block动态获取的
    int argCount = DDArgCount(str);
    ffi_type **argTypes = _allocate(argCount * sizeof(*argTypes));
    
    int i = -1; // 第一个是返回值，需要排除
    while(str && *str)
    {
        const char *next = DDSizeAndAlignment(str, NULL, NULL, NULL);
        if(i >= 0)
            argTypes[i] = _ffiArgForEncode(str);
        i++;
        str = next;
    }
    
    *outCount = argCount;
    numberOfArguments = argCount;
    
    return argTypes;
}

void PrintHelloWorld() {
    NSLog(@"Hello World");
}

void PrintArguments(ffi_cif *cif, void *ret, void **args,
                    void *userdata) {
    if (!originBlock || !replaceBlock) {
        return;
    }

    NSMethodSignature *hookBlockSignature = [NSMethodSignature signatureWithObjCTypes:DDBlockTypeEncodeString((__bridge id)(replaceBlock))];
    NSMethodSignature *originalBlockSignature = [NSMethodSignature signatureWithObjCTypes:DDBlockTypeEncodeString((__bridge id)(originBlock))];
    NSInvocation *blockInvocation = [NSInvocation invocationWithMethodSignature:hookBlockSignature];
    
    if (hookBlockSignature.numberOfArguments > numberOfArguments + 1) {
        NSLog(@"Block has too many arguments. Not calling");
    }
    
    void *argBuf = NULL;
    for (NSUInteger idx = 1; idx < hookBlockSignature.numberOfArguments; idx++) {
        const char *type = [originalBlockSignature getArgumentTypeAtIndex:idx];
        NSUInteger argSize;
        NSGetSizeAndAlignment(type, &argSize, NULL);

        if (!(argBuf = reallocf(argBuf, argSize))) {
            NSLog(@"Failed to allocate memory for block invocation.");
        }
        memcpy(argBuf, args[idx], argSize);
        [blockInvocation setArgument:argBuf atIndex:idx];
    }
    
    [blockInvocation invokeWithTarget:(__bridge id _Nonnull)(replaceBlock)];
    originBlock->invoke = originInvoke;
    ffi_call(&_cif, originInvoke, ret, args);//调用原来的方法
}

void HookBlockToPrintHelloWorld(id block) {
    void *ptr = &PrintHelloWorld;
    struct _DDBlock *dBlock = (__bridge struct _DDBlock *)block;
    dBlock->invoke = ptr;
}

void HookBlockToPrintArguments(id block) {
    originBlock = (__bridge struct _DDBlock *)block;
    
    const char *str = DDBlockTypeEncodeString(block);
    
    int argCount;
    //参数类型数组
    ffi_type **argTypes = _argsWithEncodeString(str, &argCount);
    /* Allocate closure and replaceInvoke */
    void *replaceInvoke;
    _closure = ffi_closure_alloc(sizeof(ffi_closure), &replaceInvoke);
    originInvoke = originBlock->invoke;
    originBlock->invoke = replaceInvoke;
    
    if (_closure)
    {
        
        /* Initialize the cif */
        if (ffi_prep_cif(&_cif, FFI_DEFAULT_ABI, argCount,
                         _ffiArgForEncode(str), argTypes) == FFI_OK)
        {
            Argument *t = malloc(sizeof(Argument));
            t->oBlock = *originBlock;
            t->rBlock = *replaceBlock;
            /* Initialize the closure, setting stream to stdout */
            if (ffi_prep_closure_loc(_closure, &_cif, PrintArguments,
                                     &t, replaceInvoke) != FFI_OK)
            {
                NSLog(@"ffi_prep_closure error");
                abort();
            }
        }
    }
    
    /* Deallocate both closure */
    ffi_closure_free(_closure);
}

void HookEveryBlockToPrintArguments(void) {

}

@implementation HookBlockImpl

+ (void)printHelloWorld {
    void (^block)(void) = ^(void){
        NSLog(@"block invoke");
    };
    HookBlockToPrintHelloWorld(block);
    block();
}

+ (void)printArguments {
    void (^block)(int a, int b) = ^(int a, int b){
        NSLog(@"block invoke");
        NSLog(@"--%d,--%d",a,b);
    };
    
    //
    void (^printBlock)(int a, int b) = ^(int a, int b){
        NSLog(@"%d,%d",a,b);
    };
    
    replaceBlock = (__bridge struct _DDBlock *)printBlock;
    HookBlockToPrintArguments(block);
    block(50,30);
}

- (void)addFind{
    NSLog(@"Wow,find sun yun fei");
}

+ (void)printEveryBlock {
    HookEveryBlockToPrintArguments();
    
    void (^block)(void) = ^(void){
        NSLog(@"block invoke");
    };
    block();
    
    void (^block1)(int a, NSString *b) = ^(int a, NSString *b){
        NSLog(@"block invoke");
    };
    block1(123,@"aaa");

    void (^block2)(int a, NSString *b, double c) = ^(int a, NSString *b, double c){
        NSLog(@"block invoke");
    };
    block2(123,@"aaa",300.00);
    
    void (^block3)(int a, NSString *b, double c, NSInteger d) = ^(int a, NSString *b, double c, NSInteger d){
        NSLog(@"block invoke");
    };
    block3(123,@"aaa",300.00,66);
}

@end

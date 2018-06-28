//
//  HookBlockImpl.h
//  DIDI
//
//  Created by sljr-姜毅 on 16/06/2018.
//  Copyright © 2018 HHH.DH.UR. All rights reserved.
//

#import <Foundation/Foundation.h>

@interface HookBlockImpl : NSObject

/**
 Arguments of invoking the block. Need type casting.
 */
@property (nonatomic) void *_Nullable *_Null_unspecified args;
/**
 Return value of invoking the block. Need type casting.
 */
@property (nonatomic, nullable) void *retValue;

+ (void)printHelloWorld;

+ (void)printArguments;

+ (void)printEveryBlock;

@end

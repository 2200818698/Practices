assume cs: code, ds: data, ss: stack

data segment
   string db 'Hello$'
data ends 

stack segment
    
stack ends

code segment  
   start:   
   
   mov ax, data
   mov ds, ax
   mov ax, stack
   mov ss, ax
   
;   call hello   
                
;  params
   push 1122h
   push 3344h    
                
   call sum
   
   mov ax, 4c00h
   int 21h
    
code ends 

hello:   

    mov ah, 9h
    mov dx, offset string
    
    int 21h
    
    ret     
    
    
sum:
    
    push bp
    mov bp, sp
              
              
    sub sp, 4  
    
;  protect register
    push bx   
    
;  part params fill int 3 (CC)
; stosw: copy 'ax' value to 'es:di' , 'di' + 2
    mov ax, 0cccch  
    
    mov bx, ss
    mov es, bx
    
    mov di, bp
    sub di, 4
    
;   repeat number
    mov cx, 2
    
    rep stosw
              
;   part params
    mov bx,1111h
    mov [bp-4],2222h
    
    mov ax, bx    
    add ax, [bp-4]
    add ax, [bp+4]
    add ax, [bp+6]  
    
    call minus   
        
;   pop register from near address
    pop bx          
               
    mov sp, bp
    pop bp 
    
    ret
    
minus:  

    push bp
    mov bp, sp
              
              
    sub sp, 2
              
;   part params
    mov [bp-2],6666h 
    
    sub ax, [bp-2]
    
    mov sp, bp
    pop bp 
    
    ret
    

end start
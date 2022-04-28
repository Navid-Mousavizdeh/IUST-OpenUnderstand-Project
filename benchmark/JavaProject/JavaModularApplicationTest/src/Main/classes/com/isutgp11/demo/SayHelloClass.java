package com.isutgp11.demo;
/**
 * @author isutgp11
 */
public class SayHelloClass {
    static int N = 33;
    static int M = 0;
    public void sayHello() {
        System.out.println("Hello from IUST");
        if (N > 0){
            N--;
            --N;
        }
        else
        {
            M++;
            N += M * 33;
        }
    }
    public void sayGoodBye() {
        System.out.println("Hello from IUST");
        if (N > 0){
            N /= 3;
        }
        else
        {
            M++;
            N *= (M * 33);
        }
    }
    public void saynamedModule() {
        Module module = SayHelloClass.class.getModule();
        System.out.println("Module: " + module);
        System.out.println("Name: " + module.getName());
        System.out.println("isNamed: " + module.isNamed());
        System.out.println("Descriptor: " + module.getDescriptor());
    }
}

package com.calculator.app.display;

import java.lang.System;

// this class is a candidate for inline-class refactoring
// because they have not too much responsibility and there is not any plan to add new responsibility
public class print_success {

    public static void print_success_message() {
        System.out.println("operation has been done successfully");
    }
    public static void main(String[] args) {
        bool a = true, b = true, c = true;
        if (a || (b && c)) {
            while (a ? b : c) {
                for (int i = 0; i < 10; i++) {
                    if (i == 5) {
                        break;
                    }
                    switch (i) {
                        case 1:
                        case 2:
                            i++;
                            break;
                        case 5:
                            break;
                        default:
                            i++;
                    }
                }
            }
        } 
    }
}
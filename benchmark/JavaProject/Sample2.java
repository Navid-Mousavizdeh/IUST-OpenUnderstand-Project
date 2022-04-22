public class Main {
  static void myMethod2() {
    System.out.println("I just got executed!");
  }

  public static void main(String[] args) {
    myMethod2();
  }
}

class A {
  int x = 0;
  static void m2() {
    System.out.println("I just got executed!");
  }

  public static void main(String[] args) {
    m2();
  }
}
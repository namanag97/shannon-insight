// Sample Java file for testing tree-sitter parsing.
package com.example;

import java.util.List;
import java.util.ArrayList;

public interface Greeter {
    String greet(String name);
}

public abstract class BaseGreeter implements Greeter {
    protected String prefix;

    public abstract String greet(String name);
}

public class HelloGreeter extends BaseGreeter {
    public HelloGreeter(String prefix) {
        this.prefix = prefix;
    }

    @Override
    public String greet(String name) {
        return String.format("%s, %s!", prefix, name);
    }

    private void helper() {
        System.out.println("helper");
    }
}

public class DataProcessor {
    public int processData(List<Integer> data) {
        int sum = 0;
        for (int v : data) {
            if (v > 0) {
                for (int i = 0; i < v; i++) {
                    sum += i;
                }
            }
        }
        return sum;
    }

    public static void main(String[] args) {
        HelloGreeter g = new HelloGreeter("Hello");
        System.out.println(g.greet("World"));
    }
}

package com.example;

import java.util.List;
import java.util.ArrayList;

public class Hello {
    private final List<String> items = new ArrayList<>();

    public String greet(String name) {
        if (name == null) {
            name = "world";
        }
        return "hi " + name;
    }

    public int count() {
        return items.size();
    }
}

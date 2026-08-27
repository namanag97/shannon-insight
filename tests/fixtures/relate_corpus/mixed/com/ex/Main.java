package com.ex;

import com.ex.util.S;
import com.ex.core.Engine;
import com.ex.utilcodec.C;

public final class Main {
    private Main() {
    }

    public static void main(String[] args) {
        Engine e = new Engine();
        System.out.println(S.name() + e.id() + C.tag());
    }
}

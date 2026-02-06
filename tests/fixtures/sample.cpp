// Sample C++ file for testing tree-sitter parsing.

#include <iostream>
#include <string>
#include <vector>

class Greeter {
public:
    virtual ~Greeter() = default;
    virtual std::string greet(const std::string& name) const = 0;
};

class HelloGreeter : public Greeter {
private:
    std::string prefix_;

public:
    explicit HelloGreeter(const std::string& prefix = "Hello")
        : prefix_(prefix) {}

    std::string greet(const std::string& name) const override {
        return prefix_ + ", " + name + "!";
    }

private:
    void helper() const {
        std::cout << "helper" << std::endl;
    }
};

template<typename T>
T process_data(const std::vector<T>& data) {
    T sum = 0;
    for (const auto& v : data) {
        if (v > 0) {
            for (T i = 0; i < v; ++i) {
                sum += i;
            }
        }
    }
    return sum;
}

int main() {
    HelloGreeter g("Hello");
    std::cout << g.greet("World") << std::endl;
    return 0;
}

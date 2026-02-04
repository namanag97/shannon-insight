# Code Smell Detection: Comprehensive Research Document

## Executive Summary

Code smells are surface indicators that suggest deeper problems in software design. The term was coined by Kent Beck in the late 1990s and popularized by Martin Fowler in his seminal work "Refactoring: Improving the Design of Existing Code" (1999). Unlike bugs, code smells don't prevent code from functioning, but they indicate weaknesses in design that may slow development, increase maintenance costs, and elevate the risk of future bugs.

This document provides a comprehensive framework for implementing language-agnostic code smell detection, covering mathematical foundations, detection heuristics, implementation guidance, and code examples for 12+ common code smells.

**Key Findings:**
- Code smells correlate with technical debt and reduced maintainability
- Statistical outlier detection combined with syntactic analysis provides robust detection
- Universal metrics (method length, complexity, coupling) work across all programming languages
- Cyclomatic complexity thresholds: 1-10 (simple), 11-20 (moderate), 21-50 (high risk), >50 (untestable)
- God Class and Long Method are the most prevalent and impactful smells

---

## Mathematical Foundations

### 1. Complexity Metrics

#### Cyclomatic Complexity
**Definition:** The number of linearly independent paths through a program's source code.

**Formula:**
```
M = E - N + 2P
```
Where:
- E = Number of edges in control flow graph
- N = Number of nodes in control flow graph
- P = Number of connected components (usually 1 for a single method)

**Thresholds for Code Smell Detection:**
| Complexity Range | Risk Level | Code Smell Indicator |
|-----------------|-------------|---------------------|
| 1-10 | Low risk | Normal |
| 11-20 | Moderate risk | Consider review |
| 21-50 | High risk | Long Method, Complex Method |
| >50 | Very high risk | Critical - Immediate Refactoring |

**Detection Application:** Methods with cyclomatic complexity > 10 trigger Long Method or Complex Method smells.

#### Halstead Complexity Measures
**Definition:** Quantitative measures of program complexity based on operators and operands.

**Key Metrics:**
1. **Program Vocabulary:** η = η₁ + η₂
   - η₁ = Number of distinct operators
   - η₂ = Number of distinct operands

2. **Program Length:** N = N₁ + N₂
   - N₁ = Total number of operators
   - N₂ = Total number of operands

3. **Volume:** V = N × log₂η

4. **Difficulty:** D = (η₁/2) × (N₂/η₂)

5. **Effort:** E = D × V

6. **Delivered Bugs:** B = E^(2/3) / 3000 (or V/3000)

**Thresholds for Code Smell Detection:**
- Volume > 1000: Suggests overly complex code
- Difficulty > 30: Hard to understand/maintain
- Effort > 5000: High maintenance cost

**Detection Application:** High Halstead volume indicates methods that should be extracted.

### 2. Statistical Approaches

#### Method Size Distribution Analysis
**Gini Coefficient Application:**
```
G = ΣᵢΣⱼ|xᵢ - xⱼ| / (2n²μ)
```
Where:
- xᵢ, xⱼ = Method sizes
- n = Number of methods
- μ = Mean method size

**Application:** High Gini coefficient (>0.5) indicates uneven method size distribution, suggesting Long Method smells.

#### Outlier Detection Using IQR (Interquartile Range)
```
Q1 = 25th percentile of method lengths
Q3 = 75th percentile of method lengths
IQR = Q3 - Q1
Upper Threshold = Q3 + 1.5 × IQR
Lower Threshold = Q1 - 1.5 × IQR
```

**Application:** Methods with length > Upper Threshold are statistical outliers and candidates for Long Method smell.

#### Z-Score Normalization
```
Z = (x - μ) / σ
```
Where:
- x = Metric value (method length, complexity)
- μ = Mean value
- σ = Standard deviation

**Application:** |Z| > 3 indicates extreme outliers (3-sigma rule).

### 3. Information Theory in Code Duplication Detection

#### Similarity Metrics
**Levenshtein Distance:**
```
D(i,j) = min {
  D(i-1, j) + 1,
  D(i, j-1) + 1,
  D(i-1, j-1) + (s₁[i] ≠ s₂[j] ? 1 : 0)
}
```

**Jaccard Similarity:**
```
J(A,B) = |A ∩ B| / |A ∪ B|
```

**Detection Threshold:**
- Exact duplicates: Similarity = 1.0
- Type 1 clones (exact with renaming): Similarity > 0.95
- Type 2 clones (syntactic variations): Similarity > 0.85
- Type 3 clones (similar logic): Similarity > 0.70

**Application:** Code blocks with similarity > 0.85 flagged as Duplicate Code smell.

### 4. Coupling Metrics

#### Lack of Cohesion of Methods (LCOM)
**Original Henderson-Sellers Formula:**
```
LCOM = |{P|P∩I = ∅}| / |{P}|
```
Where:
- P = Set of method pairs
- I = Set of method pairs that share at least one instance variable

**Thresholds:**
- LCOM > 0.75: Poor cohesion (possible God Class)
- LCOM < 0.25: Good cohesion

**Application:** High LCOM with many methods suggests God Class smell.

---

## Language-Agnostic Design

### Universal Code Smells

Code smells that are **language-independent** and can be detected across all programming languages through syntactic and structural analysis:

1. **Long Method** - Excessive number of statements/lines
2. **God Class** - Too many responsibilities, methods, or dependencies
3. **Duplicate Code** - Repeated code fragments
4. **Feature Envy** - Method accesses more data from other classes than its own
5. **Data Clumps** - Groups of parameters always passed together
6. **Long Parameter List** - Too many parameters to a method
7. **Shotgun Surgery** - Single change requires modifying many classes
8. **Divergent Change** - Class changed for multiple unrelated reasons
9. **Dead Code** - Unused code that will never execute
10. **Complex Method** - High cyclomatic complexity
11. **Magic Numbers** - Unnamed numeric literals
12. **Inappropriate Intimacy** - Excessive coupling between classes

### Universal Metrics Across Languages

| Metric | Language Independence | Detection Method |
|---------|---------------------|------------------|
| Method Length | ✅ Universal | Count statements/tokens |
| Cyclomatic Complexity | ✅ Universal | Count branching points |
| Parameter Count | ✅ Universal | Count parameters |
| Nesting Depth | ✅ Universal | Count indentation levels |
| Class Size | ✅ Universal | Count methods/fields |
| Coupling | ✅ Universal | Count unique class references |
| Duplication | ✅ Universal | String/token similarity |
| Code Volume | ✅ Universal | Count tokens/lines |

### Detecting God Class in Any Language

**Detection Heuristics (Language-Agnostic):**

1. **WMC (Weighted Methods per Class)** > 100
   - Sum of cyclomatic complexities of all methods

2. **TCC (Tight Class Cohesion)** < 0.33
   - Low cohesion indicates many unrelated responsibilities

3. **ATFD (Access to Foreign Data)** > Few
   - Methods frequently access other classes' data

4. **Method Count** > 15-20
   - Absolute number of methods

5. **Field Count** > 20-30
   - Absolute number of instance variables

**Detection Algorithm:**
```
IF (class.methods.count > 15 AND
    class.fields.count > 20 AND
    average(methods.complexity) > 5 AND
    class.cohesion < 0.4) THEN
    RETURN "God Class detected"
```

### Identifying Feature Envy Across Languages

**Detection Heuristics:**

1. **External Data Access Ratio:**
```
EDAR = (Accesses to foreign class fields) / (Total data accesses)
```

2. **Detection Threshold:**
```
IF EDAR > 0.5 THEN
    Method likely has Feature Envy
```

3. **Method Access Pattern Analysis:**
   - Count method calls to other classes vs. own class
   - Count field accesses to other classes vs. own class

**Language-Agnostic Detection:**
```python
def detect_feature_envy(method):
    own_class_accesses = count_class_accesses(method, method.class_name)
    foreign_accesses = count_foreign_class_accesses(method)
    total = own_class_accesses + foreign_accesses

    if total > 0 and (foreign_accesses / total) > 0.5:
        return True, "Feature Envy"
    return False, None
```

---

## Code Smell Catalog

### 1. Long Method

**Description:** A method contains too many lines of code, making it difficult to understand, test, and maintain.

**Mathematical Detection:**
- **Primary Metric:** Lines of code or statement count
- **Threshold:** > 50-100 lines (depending on language and project standards)
- **Supporting Metric:** Cyclomatic complexity > 10
- **Statistical Method:** Top 10% of methods by length in codebase

**Detection Algorithm:**
```
function detect_long_method(method):
    loc = count_lines_of_code(method)
    complexity = calculate_cyclomatic_complexity(method)

    if loc > threshold AND complexity > 10:
        return "Long Method"
    if loc > statistical_upper_bound:
        return "Long Method (statistical outlier)"
    return None
```

**Code Example (Before):**
```javascript
function processOrder(order) {
    let result = {};
    result.id = generateId();
    result.customer = order.customerId;
    result.items = [];
    result.total = 0;
    result.tax = 0;
    result.shipping = 0;
    result.discount = 0;
    result.status = 'pending';
    result.createdAt = new Date();

    for (let item of order.items) {
        let product = getProduct(item.productId);
        let lineTotal = product.price * item.quantity;
        result.items.push({
            productId: item.productId,
            name: product.name,
            price: product.price,
            quantity: item.quantity,
            total: lineTotal
        });
        result.total += lineTotal;
    }

    result.tax = result.total * 0.1;
    result.shipping = calculateShipping(order.shippingAddress);

    if (order.couponCode) {
        let coupon = validateCoupon(order.couponCode);
        if (coupon) {
            result.discount = result.total * coupon.discountPercentage;
        }
    }

    result.total = result.total + result.shipping + result.tax - result.discount;

    if (result.total < 0) {
        result.total = 0;
    }

    saveOrder(result);
    sendConfirmationEmail(result);
    updateInventory(result);
    return result;
}
```

**Refactored Code (After):**
```javascript
function processOrder(order) {
    let result = createOrderBase(order);
    result.items = processOrderItems(order.items);
    result.total = calculateSubtotal(result.items);
    result.tax = calculateTax(result.total);
    result.shipping = calculateShipping(order.shippingAddress);
    result.discount = applyCoupon(order.couponCode, result.total);
    result.total = finalizeTotal(result.total, result.tax, result.shipping, result.discount);
    finalizeOrder(result);
    return result;
}

function createOrderBase(order) {
    return {
        id: generateId(),
        customer: order.customerId,
        status: 'pending',
        createdAt: new Date()
    };
}

function processOrderItems(items) {
    return items.map(item => {
        let product = getProduct(item.productId);
        return {
            productId: item.productId,
            name: product.name,
            price: product.price,
            quantity: item.quantity,
            total: product.price * item.quantity
        };
    });
}

function calculateSubtotal(items) {
    return items.reduce((sum, item) => sum + item.total, 0);
}

function calculateTax(subtotal) {
    return subtotal * 0.1;
}

function finalizeTotal(subtotal, tax, shipping, discount) {
    let total = subtotal + tax + shipping - discount;
    return Math.max(0, total);
}
```

**Refactoring Technique:** Extract Method

---

### 2. God Class (Large Class)

**Description:** A class that's too large, knows too much, or does too much. It exhibits low cohesion and high coupling.

**Mathematical Detection:**
- **Primary Metric:** WMC (Weighted Methods per Class) > 100
- **Secondary Metrics:**
  - Method count > 15-20
  - Field count > 20-30
  - TCC (Tight Class Cohesion) < 0.33
  - LCOM4 (Lack of Cohesion) > 0.75

**Detection Algorithm:**
```
function detect_god_class(cls):
    wmc = sum(method.complexity for method in cls.methods)
    cohesion = calculate_class_cohesion(cls)

    if (cls.methods.length > 15 AND
        cls.fields.length > 20 AND
        wmc > 100 AND
        cohesion < 0.4):
        return "God Class"
    return None
```

**Code Example (Before):**
```python
class OrderManager:
    def __init__(self):
        self.orders = []
        self.customers = []
        self.products = []
        self.db_connection = DatabaseConnection()

    def create_order(self, customer_id, items):
        customer = self.get_customer(customer_id)
        order = {'customer': customer, 'items': items}
        total = self.calculate_total(items)
        order['total'] = total
        tax = self.calculate_tax(total)
        order['tax'] = tax
        order_id = self.save_to_db(order)
        self.send_email(customer['email'], order_id)
        self.update_inventory(items)
        self.orders.append(order)
        return order_id

    def get_customer(self, customer_id):
        query = f"SELECT * FROM customers WHERE id = {customer_id}"
        return self.db_connection.execute(query)

    def calculate_total(self, items):
        total = 0
        for item in items:
            product = self.get_product(item['product_id'])
            total += product['price'] * item['quantity']
        return total

    def calculate_tax(self, amount):
        return amount * 0.1

    def save_to_db(self, order):
        query = f"INSERT INTO orders VALUES (...)"
        return self.db_connection.execute(query)

    def send_email(self, email, order_id):
        # Email sending logic
        EmailService.send(to=email, subject=f"Order {order_id}")

    def update_inventory(self, items):
        for item in items:
            self.db_connection.execute(
                f"UPDATE products SET stock = stock - {item['quantity']} "
                f"WHERE id = {item['product_id']}"
            )

    def get_product(self, product_id):
        return next(p for p in self.products if p['id'] == product_id)

    def process_payment(self, order_id, payment_details):
        order = self.get_order(order_id)
        if not order:
            raise Exception("Order not found")
        result = PaymentGateway.charge(payment_details, order['total'])
        if result['success']:
            self.update_order_status(order_id, 'paid')
        return result

    def get_order(self, order_id):
        query = f"SELECT * FROM orders WHERE id = {order_id}"
        return self.db_connection.execute(query)

    def update_order_status(self, order_id, status):
        query = f"UPDATE orders SET status = '{status}' WHERE id = {order_id}"
        self.db_connection.execute(query)

    def generate_report(self, start_date, end_date):
        query = f"SELECT * FROM orders WHERE date BETWEEN '{start_date}' AND '{end_date}'"
        orders = self.db_connection.execute(query)
        report = {'total': 0, 'count': len(orders), 'orders': orders}
        for order in orders:
            report['total'] += order['total']
        return report

    # ... 10+ more methods handling various responsibilities
```

**Refactored Code (After):**
```python
# order_service.py
class OrderService:
    def __init__(self, order_repository, pricing_service, email_service):
        self.order_repository = order_repository
        self.pricing_service = pricing_service
        self.email_service = email_service

    def create_order(self, customer_id, items):
        order = Order(customer_id, items)
        total = self.pricing_service.calculate_total(items)
        order.set_total(total)
        tax = self.pricing_service.calculate_tax(total)
        order.set_tax(tax)
        order_id = self.order_repository.save(order)
        self.email_service.send_confirmation(customer_id, order_id)
        return order_id


# order.py
class Order:
    def __init__(self, customer_id, items):
        self.customer_id = customer_id
        self.items = items
        self.status = 'pending'

    def set_total(self, total):
        self.total = total

    def set_tax(self, tax):
        self.tax = tax

    def get_total_with_tax(self):
        return self.total + self.tax


# pricing_service.py
class PricingService:
    def calculate_total(self, items):
        return sum(item['price'] * item['quantity'] for item in items)

    def calculate_tax(self, amount):
        return amount * 0.1

    def calculate_shipping(self, address):
        # Shipping calculation logic
        pass


# order_repository.py
class OrderRepository:
    def __init__(self, db_connection):
        self.db = db_connection

    def save(self, order):
        # Save to database
        pass

    def find_by_id(self, order_id):
        # Find order in database
        pass


# inventory_service.py
class InventoryService:
    def __init__(self, db_connection):
        self.db = db_connection

    def update_for_order(self, items):
        for item in items:
            self.db.execute(
                f"UPDATE products SET stock = stock - {item['quantity']} "
                f"WHERE id = {item['product_id']}"
            )


# payment_service.py
class PaymentService:
    def process_payment(self, order, payment_details):
        result = PaymentGateway.charge(payment_details, order.total_with_tax)
        if result['success']:
            order.status = 'paid'
        return result
```

**Refactoring Techniques:** Extract Class, Extract Superclass, Replace Type Code with Subclasses

---

### 3. Duplicate Code

**Description:** Identical or very similar code exists in multiple locations. This violates the DRY (Don't Repeat Yourself) principle.

**Mathematical Detection:**
- **Similarity Threshold:** > 0.85 for Type 1-2 clones
- **Minimum Clone Length:** 6-10 tokens/lines (to avoid flagging trivial code)
- **Detection Methods:**
  - Token-based similarity (exact match with renaming)
  - AST-based similarity (structural matching)
  - Metric-based (Levenshtein distance, Jaccard similarity)

**Detection Algorithm:**
```
function detect_duplicate_code(codebase):
    clones = []
    token_blocks = extract_token_blocks(codebase, min_length=6)

    for i in range(len(token_blocks)):
        for j in range(i + 1, len(token_blocks)):
            similarity = calculate_similarity(token_blocks[i], token_blocks[j])
            if similarity > 0.85:
                clones.append({
                    'block1': token_blocks[i],
                    'block2': token_blocks[j],
                    'similarity': similarity
                })

    return deduplicate_clones(clones)
```

**Code Example (Before):**
```java
public class OrderProcessor {
    public void processOrder(Order order) {
        // Validate order
        if (order.getCustomer() == null) {
            throw new ValidationException("Customer is required");
        }
        if (order.getItems().isEmpty()) {
            throw new ValidationException("Order must have items");
        }
        if (order.getTotal() <= 0) {
            throw new ValidationException("Order total must be positive");
        }

        // Save order
        String query = "INSERT INTO orders (customer_id, total) VALUES (?, ?)";
        database.execute(query, order.getCustomer().getId(), order.getTotal());

        // Send notification
        EmailService.send(order.getCustomer().getEmail(),
                       "Order Confirmation",
                       "Your order has been received");
    }

    public void processRefund(Refund refund) {
        // Validate refund
        if (refund.getCustomer() == null) {
            throw new ValidationException("Customer is required");
        }
        if (refund.getAmount() <= 0) {
            throw new ValidationException("Refund amount must be positive");
        }
        if (refund.getOrder() == null) {
            throw new ValidationException("Order is required");
        }

        // Save refund
        String query = "INSERT INTO refunds (customer_id, amount) VALUES (?, ?)";
        database.execute(query, refund.getCustomer().getId(), refund.getAmount());

        // Send notification
        EmailService.send(refund.getCustomer().getEmail(),
                       "Refund Confirmation",
                       "Your refund has been processed");
    }
}
```

**Refactored Code (After):**
```java
public class OrderProcessor {
    public void processOrder(Order order) {
        validateCustomer(order.getCustomer());
        validateOrderItems(order.getItems());
        validatePositiveTotal(order.getTotal());

        String query = "INSERT INTO orders (customer_id, total) VALUES (?, ?)";
        database.execute(query, order.getCustomer().getId(), order.getTotal());

        sendNotification(order.getCustomer().getEmail(),
                      "Order Confirmation",
                      "Your order has been received");
    }

    public void processRefund(Refund refund) {
        validateCustomer(refund.getCustomer());
        validatePositiveAmount(refund.getAmount());
        validateOrderExists(refund.getOrder());

        String query = "INSERT INTO refunds (customer_id, amount) VALUES (?, ?)";
        database.execute(query, refund.getCustomer().getId(), refund.getAmount());

        sendNotification(refund.getCustomer().getEmail(),
                      "Refund Confirmation",
                      "Your refund has been processed");
    }

    private void validateCustomer(Customer customer) {
        if (customer == null) {
            throw new ValidationException("Customer is required");
        }
    }

    private void validateOrderItems(List<OrderItem> items) {
        if (items.isEmpty()) {
            throw new ValidationException("Order must have items");
        }
    }

    private void validatePositiveTotal(double total) {
        if (total <= 0) {
            throw new ValidationException("Order total must be positive");
        }
    }

    private void validatePositiveAmount(double amount) {
        if (amount <= 0) {
            throw new ValidationException("Amount must be positive");
        }
    }

    private void validateOrderExists(Order order) {
        if (order == null) {
            throw new ValidationException("Order is required");
        }
    }

    private void sendNotification(String email, String subject, String body) {
        EmailService.send(email, subject, body);
    }
}
```

**Refactoring Technique:** Extract Method

---

### 4. Feature Envy

**Description:** A method that accesses more data from another class than its own, indicating it should be moved.

**Mathematical Detection:**
- **External Data Access Ratio (EDAR):**
  ```
  EDAR = (Foreign field accesses + Foreign method calls) / Total data accesses
  ```
- **Threshold:** EDAR > 0.5 (method accesses foreign data more than 50% of the time)
- **Minimum Threshold:** At least 3+ foreign accesses to avoid false positives

**Detection Algorithm:**
```
function detect_feature_envy(method):
    own_class_accesses = count_accesses_to(method, method.own_class)
    foreign_accesses = count_all_foreign_accesses(method)
    total_accesses = own_class_accesses + foreign_accesses

    if total_accesses > 3 and (foreign_accesses / total_accesses) > 0.5:
        target_class = find_most_accessed_foreign_class(method)
        return "Feature Envy", target_class
    return None
```

**Code Example (Before):**
```javascript
class Order {
    constructor(customer, items) {
        this.customer = customer;
        this.items = items;
        this.status = 'pending';
    }

    calculateDiscount() {
        let discount = 0;
        let customerTier = this.customer.getTier();
        let orderHistory = this.customer.getOrderHistory();
        let orderCount = orderHistory.length;
        let totalSpent = orderHistory.reduce((sum, order) => sum + order.total, 0);

        if (customerTier === 'platinum' && orderCount > 10) {
            discount = 0.15;
        } else if (customerTier === 'gold' && orderCount > 5) {
            discount = 0.10;
        } else if (customerTier === 'silver' && totalSpent > 1000) {
            discount = 0.05;
        }

        return discount;
    }
}
```

**Refactored Code (After):**
```javascript
class Order {
    constructor(customer, items) {
        this.customer = customer;
        this.items = items;
        this.status = 'pending';
    }

    calculateDiscount() {
        return this.customer.calculateDiscountForOrder(this);
    }
}

class Customer {
    constructor(name, tier, email) {
        this.name = name;
        this.tier = tier;
        this.email = email;
        this.orderHistory = [];
    }

    calculateDiscountForOrder(order) {
        let orderCount = this.orderHistory.length;
        let totalSpent = this.orderHistory.reduce((sum, o) => sum + o.total, 0);

        if (this.tier === 'platinum' && orderCount > 10) {
            return 0.15;
        } else if (this.tier === 'gold' && orderCount > 5) {
            return 0.10;
        } else if (this.tier === 'silver' && totalSpent > 1000) {
            return 0.05;
        }

        return 0;
    }
}
```

**Refactoring Technique:** Move Method

---

### 5. Data Clumps

**Description:** Groups of variables (parameters or fields) that always travel together. This suggests they should be encapsulated as an object.

**Mathematical Detection:**
- **Co-occurrence Frequency:** Parameters/fields appearing together > 3 times
- **Correlation Analysis:** High correlation (> 0.7) between usage patterns
- **Detection Method:** Frequent itemset mining (Apriori algorithm)

**Detection Algorithm:**
```
function detect_data_clumps(methods):
    parameter_signatures = [get_parameters(m) for m in methods]
    candidate_clumps = find_frequent_combinations(parameter_signatures, min_support=3)

    data_clumps = []
    for clump in candidate_clumps:
        if len(clump) >= 2:
            data_clumps.append({
                'variables': clump,
                'occurrences': count_occurrences(clump, parameter_signatures)
            })

    return data_clumps
```

**Code Example (Before):**
```python
def create_user(username, email, first_name, last_name, address, city, state, zip_code):
    user = User(username, email)
    profile = UserProfile(first_name, last_name)
    address_obj = Address(address, city, state, zip_code)
    user.save()
    return user

def update_user(user_id, username, email, first_name, last_name, address, city, state, zip_code):
    user = User.get(user_id)
    user.username = username
    user.email = email
    user.profile.first_name = first_name
    user.profile.last_name = last_name
    user.profile.address = address
    user.profile.city = city
    user.profile.state = state
    user.profile.zip_code = zip_code
    user.save()

def send_welcome_email(username, email, first_name, last_name, address, city, state, zip_code):
    # Send welcome email with all user info
    pass
```

**Refactored Code (After):**
```python
@dataclass
class ContactInfo:
    username: str
    email: str

@dataclass
class Name:
    first_name: str
    last_name: str

@dataclass
class Address:
    street: str
    city: str
    state: str
    zip_code: str

def create_user(contact: ContactInfo, name: Name, address: Address):
    user = User(contact.username, contact.email)
    profile = UserProfile(name.first_name, name.last_name)
    address_obj = Address(address.street, address.city,
                      address.state, address.zip_code)
    user.save()
    return user

def update_user(user_id: int, contact: ContactInfo, name: Name, address: Address):
    user = User.get(user_id)
    user.username = contact.username
    user.email = contact.email
    user.profile.first_name = name.first_name
    user.profile.last_name = name.last_name
    user.profile.address = address.street
    user.profile.city = address.city
    user.profile.state = address.state
    user.profile.zip_code = address.zip_code
    user.save()

def send_welcome_email(contact: ContactInfo, name: Name, address: Address):
    # Send welcome email
    pass
```

**Refactoring Technique:** Introduce Parameter Object

---

### 6. Long Parameter List

**Description:** A method has too many parameters, making it hard to understand and call.

**Mathematical Detection:**
- **Primary Metric:** Parameter count > 4-7
- **Statistical Method:** Top 10% of methods by parameter count
- **Threshold:**
  - 1-3 parameters: Normal
  - 4-5 parameters: Warning
  - 6+ parameters: Code smell

**Detection Algorithm:**
```
function detect_long_parameter_list(method):
    param_count = len(method.parameters)

    if param_count > 7:
        return "Long Parameter List (Critical)"
    elif param_count >= 5:
        return "Long Parameter List (Warning)"
    elif param_count > statistical_p95:
        return "Long Parameter List (Statistical)"

    return None
```

**Code Example (Before):**
```java
public void createEmployee(String firstName, String lastName,
                      String email, String phone,
                      String department, String position,
                      double salary, Date hireDate,
                      boolean isFullTime, String manager) {
    Employee employee = new Employee();
    employee.setFirstName(firstName);
    employee.setLastName(lastName);
    employee.setEmail(email);
    employee.setPhone(phone);
    employee.setDepartment(department);
    employee.setPosition(position);
    employee.setSalary(salary);
    employee.setHireDate(hireDate);
    employee.setFullTime(isFullTime);
    employee.setManager(manager);
    employeeRepository.save(employee);
}
```

**Refactored Code (After):**
```java
// Option 1: Using Parameter Objects
public void createEmployee(EmployeeInfo info) {
    Employee employee = new Employee();
    employee.setFirstName(info.getFirstName());
    employee.setLastName(info.getLastName());
    employee.setEmail(info.getEmail());
    employee.setPhone(info.getPhone());
    employee.setDepartment(info.getDepartment());
    employee.setPosition(info.getPosition());
    employee.setSalary(info.getSalary());
    employee.setHireDate(info.getHireDate());
    employee.setFullTime(info.isFullTime());
    employee.setManager(info.getManager());
    employeeRepository.save(employee);
}

public class EmployeeInfo {
    private String firstName;
    private String lastName;
    private String email;
    private String phone;
    private String department;
    private String position;
    private double salary;
    private Date hireDate;
    private boolean isFullTime;
    private String manager;

    // Getters and setters
}

// Option 2: Using Builder Pattern
Employee employee = Employee.builder()
    .firstName("John")
    .lastName("Doe")
    .email("john@example.com")
    .phone("555-1234")
    .department("Engineering")
    .position("Developer")
    .salary(75000)
    .hireDate(new Date())
    .fullTime(true)
    .manager("Jane Smith")
    .build();
```

**Refactoring Techniques:** Introduce Parameter Object, Preserve Whole Object, Replace Parameter with Method

---

### 7. Shotgun Surgery

**Description:** Every time you make a kind of change, you have to make many little changes to many different classes.

**Mathematical Detection:**
- **Change Impact Analysis:** Classes that change together frequently
- **Coupling Metric:** Number of classes that would need to change for a given change
- **Threshold:** Changes affecting > 3-4 unrelated classes

**Detection Algorithm:**
```
function detect_shotgun_surgery(codebase_history):
    change_groups = group_similar_changes(codebase_history)

    high_impact_changes = []
    for change in change_groups:
        affected_classes = count_unique_classes_affected(change)
        if affected_classes > 4:
            high_impact_changes.append({
                'change': change,
                'affected_classes': affected_classes
            })

    return high_impact_changes
```

**Code Example (Before):**
```javascript
// To change customer name, need to update multiple places

// In CustomerService.js
function updateCustomerName(customerId, newName) {
    const customer = db.findCustomer(customerId);
    customer.name = newName;
    db.updateCustomer(customer);
}

// In OrderService.js
function updateCustomerNameInOrders(customerId, newName) {
    const orders = db.findOrdersByCustomer(customerId);
    orders.forEach(order => {
        order.customerName = newName;
        db.updateOrder(order);
    });
}

// In InvoiceService.js
function updateCustomerNameInInvoices(customerId, newName) {
    const invoices = db.findInvoicesByCustomer(customerId);
    invoices.forEach(invoice => {
        invoice.customerName = newName;
        db.updateInvoice(invoice);
    });
}

// In ShippingService.js
function updateCustomerNameInShipments(customerId, newName) {
    const shipments = db.findShipmentsByCustomer(customerId);
    shipments.forEach(shipment => {
        shipment.customerName = newName;
        db.updateShipment(shipment);
    });
}
```

**Refactored Code (After):**
```javascript
// Centralized customer management
class CustomerRepository {
    updateCustomerName(customerId, newName) {
        const customer = this.db.findCustomer(customerId);
        customer.name = newName;
        this.db.updateCustomer(customer);

        // Cascade updates handled by database relationships
        // Or use domain events for eventual consistency
    }
}

// Orders, invoices, shipments reference customer by ID
class Order {
    constructor(customerId) {
        this.customerId = customerId;
        this.customerName = null; // Computed from customer reference
    }

    getCustomerName() {
        return this.customer ? this.customer.name : null;
    }
}
```

**Refactoring Techniques:** Move Method, Move Field, Inline Class, Combine Classes

---

### 8. Divergent Change

**Description:** A class has to change for different reasons (e.g., changing DB schema, changing business logic, changing UI).

**Mathematical Detection:**
- **Change Category Analysis:** Number of distinct change reasons per class
- **Metric:** Class Change Entropy
  ```
  Entropy = -Σ (pᵢ × log₂pᵢ)
  ```
  Where pᵢ = proportion of changes of type i
- **Threshold:** Classes with > 2-3 distinct change categories

**Detection Algorithm:**
```
function detect_divergent_change(change_history):
    class_changes = categorize_changes_by_class(change_history)

    problematic_classes = []
    for cls, changes in class_changes.items():
        categories = set(change.category for change in changes)
        if len(categories) >= 3:
            problematic_classes.append({
                'class': cls,
                'categories': categories,
                'change_count': len(changes)
            })

    return problematic_classes
```

**Code Example (Before):**
```python
class ReportGenerator:
    def __init__(self, database, email_service, file_system):
        self.db = database
        self.email = email_service
        self.fs = file_system

    # Database-related changes
    def generate_sales_report(self, start_date, end_date):
        query = f"SELECT * FROM sales WHERE date BETWEEN '{start_date}' AND '{end_date}'"
        results = self.db.execute(query)
        return self.format_results(results)

    # Business logic changes
    def calculate_commission(self, sales_data):
        total = 0
        for sale in sales_data:
            if sale['amount'] > 1000:
                total += sale['amount'] * 0.1
            else:
                total += sale['amount'] * 0.05
        return total

    # Email-related changes
    def send_report_email(self, recipient, report_data):
        body = self.format_email_body(report_data)
        self.email.send(recipient, "Sales Report", body)

    # File system changes
    def save_report_to_file(self, report_data, filename):
        content = self.format_file_content(report_data)
        self.fs.write(filename, content)

    # UI/formatting changes
    def format_results(self, results):
        return [{"date": r['date'], "amount": r['amount']} for r in results]

    def format_email_body(self, data):
        return "\n".join([f"{d['date']}: {d['amount']}" for d in data])

    def format_file_content(self, data):
        return ",".join([f"{d['date']},{d['amount']}" for d in data])
```

**Refactored Code (After):**
```python
# Data access layer
class SalesRepository:
    def __init__(self, database):
        self.db = database

    def find_sales_by_date_range(self, start_date, end_date):
        query = f"SELECT * FROM sales WHERE date BETWEEN '{start_date}' AND '{end_date}'"
        return self.db.execute(query)

# Business logic layer
class CommissionCalculator:
    def calculate(self, sales_data):
        total = 0
        for sale in sales_data:
            rate = 0.1 if sale['amount'] > 1000 else 0.05
            total += sale['amount'] * rate
        return total

# Presentation layer
class ReportFormatter:
    def format_for_display(self, results):
        return [{"date": r['date'], "amount": r['amount']} for r in results]

    def format_for_email(self, data):
        return "\n".join([f"{d['date']}: {d['amount']}" for d in data])

    def format_for_csv(self, data):
        return ",".join([f"{d['date']},{d['amount']}" for d in data])

# Service layer - coordinates other layers
class ReportService:
    def __init__(self, repository, calculator, formatter):
        self.repository = repository
        self.calculator = calculator
        self.formatter = formatter

    def generate_sales_report(self, start_date, end_date):
        sales_data = self.repository.find_sales_by_date_range(start_date, end_date)
        commission = self.calculator.calculate(sales_data)
        return self.formatter.format_for_display(sales_data)
```

**Refactoring Techniques:** Extract Class, Split Class

---

### 9. Dead Code

**Description:** Code that is never executed, either unreachable or never called.

**Mathematical Detection:**
- **Call Graph Analysis:** Methods/functions never referenced
- **Control Flow Analysis:** Unreachable code paths
- **Liveness Analysis:** Variables/fields never read

**Detection Algorithm:**
```
function detect_dead_code(codebase):
    call_graph = build_call_graph(codebase)
    reachable_nodes = find_reachable_from_entry_points(call_graph)

    dead_methods = []
    for method in codebase.all_methods():
        if method not in reachable_nodes and not is_entry_point(method):
            dead_methods.append(method)

    dead_fields = detect_unread_fields(codebase)
    dead_parameters = detect_unused_parameters(codebase)

    return {
        'methods': dead_methods,
        'fields': dead_fields,
        'parameters': dead_parameters
    }
```

**Code Example (Before):**
```typescript
class UserService {
    private users: Map<number, User>;

    constructor() {
        this.users = new Map();
        this.initializeAdmin();
        this.loadLegacyData(); // Never called again
    }

    public getUser(id: number): User | undefined {
        return this.users.get(id);
    }

    public addUser(user: User): void {
        this.users.set(user.id, user);
    }

    private initializeAdmin(): void {
        this.addUser({
            id: 0,
            name: 'admin',
            email: 'admin@example.com'
        });
    }

    private loadLegacyData(): void {
        // This was for migration, never used now
        const legacyData = LegacySystem.fetch();
        legacyData.forEach(data => {
            this.addUser(data);
        });
    }

    private unusedHelper(value: string): string {
        // Never used anywhere
        return value.toUpperCase();
    }

    private anotherUnusedMethod(): void {
        // Also never used
        console.log('This is dead code');
    }

    public activeMethod(): void {
        // This is actively used
        console.log('Active method');
    }
}
```

**Refactored Code (After):**
```typescript
class UserService {
    private users: Map<number, User>;

    constructor() {
        this.users = new Map();
        this.initializeAdmin();
    }

    public getUser(id: number): User | undefined {
        return this.users.get(id);
    }

    public addUser(user: User): void {
        this.users.set(user.id, user);
    }

    public activeMethod(): void {
        console.log('Active method');
    }

    private initializeAdmin(): void {
        this.addUser({
            id: 0,
            name: 'admin',
            email: 'admin@example.com'
        });
    }
}

// Dead code removed:
// - loadLegacyData()
// - unusedHelper()
// - anotherUnusedMethod()
```

**Refactoring Technique:** Remove Dead Code

---

### 10. Complex Method

**Description:** A method with high cyclomatic complexity due to many branching points and nested conditions.

**Mathematical Detection:**
- **Primary Metric:** Cyclomatic complexity > 10
- **Secondary Metrics:**
  - Nesting depth > 4-5
  - Conditional statements > 5-7
  - Return statements > 3-4

**Detection Algorithm:**
```
function detect_complex_method(method):
    complexity = calculate_cyclomatic_complexity(method)
    nesting_depth = calculate_max_nesting_depth(method)
    conditionals = count_conditional_statements(method)

    if complexity > 20:
        return "Complex Method (Critical)"
    elif complexity > 10 or nesting_depth > 5:
        return "Complex Method (Warning)"

    return None
```

**Code Example (Before):**
```java
public double calculatePremium(Customer customer, Policy policy) {
    double premium = policy.getBaseRate();

    if (customer.getAge() < 25) {
        if (policy.getType() == PolicyType.AUTO) {
            premium *= 1.5;
        } else if (policy.getType() == PolicyType.HOME) {
            premium *= 1.3;
        } else if (policy.getType() == PolicyType.LIFE) {
            premium *= 1.2;
        }
    } else if (customer.getAge() < 50) {
        if (policy.getType() == PolicyType.AUTO) {
            premium *= 1.2;
        } else if (policy.getType() == PolicyType.HOME) {
            premium *= 1.1;
        } else if (policy.getType() == PolicyType.LIFE) {
            premium *= 1.05;
        }
    } else {
        if (policy.getType() == PolicyType.AUTO) {
            premium *= 1.0;
        } else if (policy.getType() == PolicyType.HOME) {
            premium *= 1.0;
        } else if (policy.getType() == PolicyType.LIFE) {
            premium *= 1.0;
        }
    }

    if (customer.hasClaims()) {
        if (customer.getClaimCount() == 1) {
            premium *= 1.3;
        } else if (customer.getClaimCount() == 2) {
            premium *= 1.5;
        } else {
            premium *= 2.0;
        }
    }

    if (policy.getTerm() > 1) {
        if (policy.getTerm() < 5) {
            premium *= 0.95;
        } else if (policy.getTerm() < 10) {
            premium *= 0.90;
        } else {
            premium *= 0.85;
        }
    }

    return premium;
}
```

**Refactored Code (After):**
```java
public double calculatePremium(Customer customer, Policy policy) {
    double premium = policy.getBaseRate();
    premium = applyAgeFactor(premium, customer.getAge(), policy.getType());
    premium = applyClaimsFactor(premium, customer.getClaimsCount());
    premium = applyTermFactor(premium, policy.getTerm());
    return premium;
}

private double applyAgeFactor(double premium, int age, PolicyType type) {
    Map<PolicyType, Double> factors = getAgeFactors(age);
    Double factor = factors.get(type);
    return premium * factor;
}

private Map<PolicyType, Double> getAgeFactors(int age) {
    if (age < 25) {
        return Map.of(
            PolicyType.AUTO, 1.5,
            PolicyType.HOME, 1.3,
            PolicyType.LIFE, 1.2
        );
    } else if (age < 50) {
        return Map.of(
            PolicyType.AUTO, 1.2,
            PolicyType.HOME, 1.1,
            PolicyType.LIFE, 1.05
        );
    } else {
        return Map.of(
            PolicyType.AUTO, 1.0,
            PolicyType.HOME, 1.0,
            PolicyType.LIFE, 1.0
        );
    }
}

private double applyClaimsFactor(double premium, int claimCount) {
    if (claimCount == 0) {
        return premium;
    } else if (claimCount == 1) {
        return premium * 1.3;
    } else if (claimCount == 2) {
        return premium * 1.5;
    } else {
        return premium * 2.0;
    }
}

private double applyTermFactor(double premium, int term) {
    if (term <= 1) {
        return premium;
    } else if (term < 5) {
        return premium * 0.95;
    } else if (term < 10) {
        return premium * 0.90;
    } else {
        return premium * 0.85;
    }
}
```

**Refactoring Techniques:** Extract Method, Decompose Conditional, Replace Conditional with Polymorphism

---

### 11. Magic Numbers

**Description:** Unnamed numeric literals scattered throughout the code, making it hard to understand their purpose and modify them consistently.

**Mathematical Detection:**
- **Pattern Matching:** Numeric literals not associated with named constants
- **Frequency:** Numbers appearing > 2 times without constants
- **Exception:** 0, 1, -1, and powers of 2 often exempt

**Detection Algorithm:**
```
function detect_magic_numbers(code):
    number_literals = extract_number_literals(code)

    magic_numbers = []
    for literal in number_literals:
        if not is_common_exception(literal) and
           not has_associated_constant(literal):
            occurrences = count_occurrences(literal, code)
            if occurrences >= 2:
                magic_numbers.append({
                    'value': literal,
                    'occurrences': occurrences,
                    'locations': find_locations(literal, code)
                })

    return magic_numbers
```

**Code Example (Before):**
```python
def calculate_tax(amount):
    return amount * 0.0825

def calculate_shipping(weight):
    if weight < 5:
        return 5.99
    elif weight < 10:
        return 9.99
    else:
        return 14.99

def calculate_discount(total):
    if total > 100:
        return total * 0.15
    elif total > 50:
        return total * 0.10
    else:
        return 0

def format_date(date):
    return date.strftime("%Y-%m-%d")

def calculate_interest(principal, rate, years):
    return principal * rate * years / 100

def max_login_attempts():
    return 3

def session_timeout():
    return 1800
```

**Refactored Code (After):**
```python
# Constants file
TAX_RATE = 0.0825
FREE_SHIPPING_THRESHOLD = 100
DISCOUNT_TIER_1 = 50
DISCOUNT_TIER_2 = 100
DISCOUNT_PERCENTAGE_TIER_1 = 0.10
DISCOUNT_PERCENTAGE_TIER_2 = 0.15
SHIPPING_LIGHT_WEIGHT = 5
SHIPPING_MEDIUM_WEIGHT = 10
SHIPPING_PRICE_LIGHT = 5.99
SHIPPING_PRICE_MEDIUM = 9.99
SHIPPING_PRICE_HEAVY = 14.99
DATE_FORMAT = "%Y-%m-%d"
INTEREST_RATE_DIVISOR = 100
MAX_LOGIN_ATTEMPTS = 3
SESSION_TIMEOUT_SECONDS = 1800

def calculate_tax(amount):
    return amount * TAX_RATE

def calculate_shipping(weight):
    if weight < SHIPPING_LIGHT_WEIGHT:
        return SHIPPING_PRICE_LIGHT
    elif weight < SHIPPING_MEDIUM_WEIGHT:
        return SHIPPING_PRICE_MEDIUM
    else:
        return SHIPPING_PRICE_HEAVY

def calculate_discount(total):
    if total > DISCOUNT_TIER_2:
        return total * DISCOUNT_PERCENTAGE_TIER_2
    elif total > DISCOUNT_TIER_1:
        return total * DISCOUNT_PERCENTAGE_TIER_1
    else:
        return 0

def format_date(date):
    return date.strftime(DATE_FORMAT)

def calculate_interest(principal, rate, years):
    return principal * rate * years / INTEREST_RATE_DIVISOR

def max_login_attempts():
    return MAX_LOGIN_ATTEMPTS

def session_timeout():
    return SESSION_TIMEOUT_SECONDS
```

**Refactoring Technique:** Replace Magic Number with Symbolic Constant

---

### 12. Inappropriate Intimacy

**Description:** Classes that know too much about each other's internals, leading to tight coupling.

**Mathematical Detection:**
- **Coupling Metric:** Number of distinct classes referenced by a class
- **Field Access:** Direct field accesses between classes (bypassing encapsulation)
- **Method Call Depth:** Chain of method calls to other classes
- **Threshold:**
  - Fan-out > 10-15 (number of classes a class depends on)
  - Direct field access to other classes > 3-5

**Detection Algorithm:**
```
function detect_inappropriate_intimacy(class_a, class_b):
    coupling_ab = count_method_calls(class_a, class_b)
    coupling_ba = count_method_calls(class_b, class_a)
    field_access_ab = count_field_accesses(class_a, class_b)
    field_access_ba = count_field_accesses(class_b, class_a)

    total_coupling = coupling_ab + coupling_ba
    total_field_access = field_access_ab + field_access_ba

    if total_coupling > 10 or total_field_access > 5:
        return "Inappropriate Intimacy", {
            'coupling': total_coupling,
            'field_access': total_field_access
        }

    return None
```

**Code Example (Before):**
```java
class Order {
    private Customer customer;
    private List<OrderItem> items;

    public void process() {
        // Inappropriate intimacy: accessing Customer internals directly
        if (this.customer.status == CustomerStatus.ACTIVE) {
            // More inappropriate intimacy
            for (OrderItem item : this.items) {
                item.product.stock = item.product.stock - item.quantity;
                item.product.save();
            }

            // Accessing internal details
            this.customer.balance = this.customer.balance - this.calculateTotal();
            this.customer.save();
        }
    }

    private double calculateTotal() {
        double total = 0;
        for (OrderItem item : this.items) {
            total += item.product.price * item.quantity;
        }
        return total;
    }
}

class Customer {
    public CustomerStatus status;
    public double balance;
    public List<Address> addresses;

    public Address getPrimaryAddress() {
        return this.addresses.get(0);
    }
}
```

**Refactored Code (After):**
```java
class Order {
    private Customer customer;
    private List<OrderItem> items;

    public void process() {
        if (this.customer.isActive()) {
            this.deductInventory();
            this.chargeCustomer();
        }
    }

    private void deductInventory() {
        this.items.forEach(item ->
            item.getProduct().deductStock(item.getQuantity())
        );
    }

    private void chargeCustomer() {
        double total = this.calculateTotal();
        this.customer.charge(total);
    }

    private double calculateTotal() {
        return this.items.stream()
            .mapToDouble(item -> item.getProduct().getPrice() * item.getQuantity())
            .sum();
    }
}

class Customer {
    private CustomerStatus status;
    private double balance;
    private List<Address> addresses;

    public boolean isActive() {
        return this.status == CustomerStatus.ACTIVE;
    }

    public void charge(double amount) {
        this.balance -= amount;
        this.save();
    }

    public Address getPrimaryAddress() {
        return this.addresses.get(0);
    }

    public double getBalance() {
        return this.balance;
    }
}

class Product {
    private double price;
    private int stock;

    public void deductStock(int quantity) {
        this.stock -= quantity;
        this.save();
    }

    public double getPrice() {
        return this.price;
    }
}
```

**Refactoring Techniques:** Hide Delegate, Move Method, Move Field

---

## Implementation Steps

### Phase 1: Setup and Analysis

1. **Define Detection Thresholds**
   - Establish project-specific thresholds based on:
     - Industry standards
     - Historical codebase analysis
     - Statistical distributions
     - Team consensus

   ```python
   # Example threshold configuration
   THRESHOLDS = {
       'long_method': {
           'lines': 50,
           'complexity': 10,
           'statistical_p90': True
       },
       'god_class': {
           'methods': 20,
           'fields': 30,
           'wmc': 100,
           'cohesion': 0.4
       },
       'duplicate_code': {
           'similarity': 0.85,
           'min_lines': 6
       }
   }
   ```

2. **Parse and Analyze Code Structure**
   - Build Abstract Syntax Trees (AST) for all source files
   - Extract metrics (method lengths, complexities, coupling)
   - Build call graphs and dependency graphs
   - Identify entry points and dead code

3. **Statistical Baseline Analysis**
   - Compute statistical distributions (mean, median, std dev, percentiles)
   - Identify statistical outliers using IQR method
   - Establish project-specific baselines

### Phase 2: Detection Implementation

4. **Implement Code Smell Detectors**
   - Create individual detectors for each smell
   - Use metric-based heuristics
   - Apply statistical outlier detection
   - Support multiple severity levels (warning, critical)

   ```python
   class CodeSmellDetector:
       def __init__(self, config):
           self.config = config

       def detect_long_method(self, method):
           loc = method.loc
           complexity = method.cyclomatic_complexity

           if loc > self.config['long_method']['lines']:
               return CodeSmell('Long Method', severity='high',
                               details={'loc': loc, 'complexity': complexity})

           if complexity > self.config['long_method']['complexity']:
               return CodeSmell('Complex Method', severity='medium',
                               details={'loc': loc, 'complexity': complexity})

           return None

       def detect_god_class(self, cls):
           if (len(cls.methods) > self.config['god_class']['methods'] and
               len(cls.fields) > self.config['god_class']['fields']):
               return CodeSmell('God Class', severity='critical',
                               details={'methods': len(cls.methods),
                                       'fields': len(cls.fields)})
           return None
   ```

5. **Implement Duplicate Code Detection**
   - Token-based detection for exact clones
   - AST-based detection for structural clones
   - Suffix array or rolling hash for efficiency
   - Minimum clone length filtering

6. **Aggregate Results**
   - Group findings by file, class, method
   - Calculate severity scores
   - Prioritize by impact and effort
   - Generate actionable reports

### Phase 3: Reporting and Feedback

7. **Generate Reports**
   - Summary dashboard with key metrics
   - Detailed listings per smell type
   - Heat maps of code quality
   - Trend analysis over time

8. **Integration with Development Workflow**
   - IDE plugins for real-time feedback
   - Pre-commit hooks
   - CI/CD integration
   - Code review annotations

### Phase 4: Continuous Improvement

9. **Tune Thresholds**
   - Monitor false positive rates
   - Gather feedback from developers
   - Adjust thresholds based on project needs
   - Track refactoring success

10. **Track Technical Debt**
    - Maintain technical debt inventory
    - Track changes over time
    - Measure refactoring ROI
    - Report to stakeholders

---

## Statistical Threshold Recommendations

### Method Length (Lines of Code)

| Percentile | Suggested Threshold | Risk Level |
|------------|-------------------|-------------|
| P50 (median) | ~15-20 lines | Normal |
| P75 | ~30-40 lines | Monitor |
| P90 | ~50-70 lines | Warning |
| P95 | ~80-100 lines | Critical |
| P99 | ~120-150 lines | Immediate action |

### Cyclomatic Complexity

| Value | Interpretation | Action Required |
|-------|--------------|----------------|
| 1-5 | Simple, easy to test | None |
| 6-10 | Moderate complexity | Review for simplification |
| 11-20 | High complexity | Consider refactoring |
| 21-50 | Very high complexity | Refactor required |
| >50 | Untestable | Immediate refactoring |

### Class Size

| Metric | Good | Warning | Critical |
|--------|-------|---------|----------|
| Number of methods | < 15 | 15-25 | > 25 |
| Number of fields | < 15 | 15-25 | > 25 |
| Lines of code | < 300 | 300-600 | > 600 |
| WMC (Weighted Methods) | < 50 | 50-100 | > 100 |

### Coupling Metrics

| Metric | Good | Warning | Critical |
|--------|-------|---------|----------|
| Fan-out (classes depended on) | < 10 | 10-15 | > 15 |
| Response for a Class (RFC) | < 20 | 20-50 | > 50 |
| Coupling Between Objects (CBO) | < 10 | 10-20 | > 20 |

### Cohesion Metrics

| Metric | Good | Warning | Poor |
|--------|-------|---------|-------|
| TCC (Tight Class Cohesion) | > 0.5 | 0.33-0.5 | < 0.33 |
| LCOM4 (Lack of Cohesion) | < 0.5 | 0.5-0.75 | > 0.75 |

---

## Implementation Example: Complete Detector

```python
import ast
import statistics
from collections import defaultdict, Counter
from typing import List, Dict, Tuple, Optional
import numpy as np

class CodeSmell:
    def __init__(self, name: str, severity: str, location: str, details: Dict):
        self.name = name
        self.severity = severity  # 'info', 'warning', 'error'
        self.location = location
        self.details = details

    def __repr__(self):
        return f"[{self.severity.upper()}] {self.name} at {self.location}"


class CodeSmellDetector:
    def __init__(self, config: Dict = None):
        self.config = config or self._default_config()
        self.metrics = defaultdict(list)

    def _default_config(self) -> Dict:
        return {
            'long_method': {'lines': 50, 'complexity': 10},
            'god_class': {'methods': 20, 'fields': 30, 'wmc': 100},
            'duplicate_code': {'similarity': 0.85, 'min_lines': 6},
            'long_parameter_list': {'parameters': 5},
            'feature_envy': {'foreign_ratio': 0.5}
        }

    def analyze_file(self, filepath: str) -> List[CodeSmell]:
        with open(filepath, 'r') as f:
            source = f.read()

        tree = ast.parse(source)
        smells = []

        # Collect metrics
        self._collect_metrics(tree, filepath)

        # Detect smells
        smells.extend(self._detect_long_methods(tree, filepath))
        smells.extend(self._detect_god_classes(tree, filepath))
        smells.extend(self._detect_magic_numbers(tree, filepath))
        smells.extend(self._detect_long_parameter_lists(tree, filepath))

        return smells

    def _collect_metrics(self, tree: ast.AST, filepath: str):
        """Collect metrics for statistical analysis"""
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                self.metrics['method_length'].append(len(node.body))
                self.metrics['method_complexity'].append(
                    self._calculate_cyclomatic_complexity(node)
                )

    def _calculate_cyclomatic_complexity(self, func: ast.FunctionDef) -> int:
        """Calculate cyclomatic complexity of a function"""
        complexity = 1  # Base complexity
        for node in ast.walk(func):
            if isinstance(node, (ast.If, ast.For, ast.While, ast.While,
                                 ast.ExceptHandler, ast.BoolOp)):
                complexity += 1
        return complexity

    def _detect_long_methods(self, tree: ast.AST, filepath: str) -> List[CodeSmell]:
        """Detect Long Method and Complex Method smells"""
        smells = []

        if not self.metrics['method_length']:
            return smells

        # Statistical thresholds
        mean_length = statistics.mean(self.metrics['method_length'])
        std_length = statistics.stdev(self.metrics['method_length'])
        upper_bound = mean_length + 2 * std_length

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                length = len(node.body)
                complexity = self._calculate_cyclomatic_complexity(node)
                location = f"{filepath}:{node.lineno}"

                if length > self.config['long_method']['lines']:
                    smells.append(CodeSmell(
                        'Long Method', 'error', location,
                        {'lines': length, 'threshold': self.config['long_method']['lines']}
                    ))

                if complexity > self.config['long_method']['complexity']:
                    smells.append(CodeSmell(
                        'Complex Method', 'warning', location,
                        {'complexity': complexity, 'threshold': self.config['long_method']['complexity']}
                    ))

                if length > upper_bound:
                    smells.append(CodeSmell(
                        'Long Method (Statistical)', 'warning', location,
                        {'lines': length, 'upper_bound': round(upper_bound, 2)}
                    ))

        return smells

    def _detect_god_classes(self, tree: ast.AST, filepath: str) -> List[CodeSmell]:
        """Detect God Class smell"""
        smells = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                methods = [n for n in node.body if isinstance(n, ast.FunctionDef)]
                fields = self._extract_class_fields(node)
                wmc = sum(self._calculate_cyclomatic_complexity(m) for m in methods)

                if (len(methods) > self.config['god_class']['methods'] or
                    len(fields) > self.config['god_class']['fields'] or
                    wmc > self.config['god_class']['wmc']):

                    location = f"{filepath}:{node.lineno}"
                    smells.append(CodeSmell(
                        'God Class', 'error', location,
                        {'methods': len(methods), 'fields': len(fields), 'wmc': wmc}
                    ))

        return smells

    def _extract_class_fields(self, cls: ast.ClassDef) -> List[str]:
        """Extract field names from a class"""
        fields = []
        for node in cls.body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name):
                        fields.append(target.id)
                    elif isinstance(target, ast.Attribute):
                        fields.append(target.attr)
        return fields

    def _detect_magic_numbers(self, tree: ast.AST, filepath: str) -> List[CodeSmell]:
        """Detect Magic Numbers smell"""
        smells = []
        number_counts = Counter()
        number_locations = defaultdict(list)

        for node in ast.walk(tree):
            if isinstance(node, ast.Constant):
                if isinstance(node.value, (int, float)):
                    # Skip common exceptions
                    if node.value in [0, 1, -1, 2, 100, 1000]:
                        continue

                    key = (type(node.value), node.value)
                    number_counts[key] += 1
                    number_locations[key].append(f"{filepath}:{node.lineno}")

        # Flag numbers appearing multiple times
        for (type_, value), count in number_counts.items():
            if count >= 2:
                for location in number_locations[(type_, value)]:
                    smells.append(CodeSmell(
                        'Magic Number', 'warning', location,
                        {'value': value, 'occurrences': count}
                    ))

        return smells

    def _detect_long_parameter_lists(self, tree: ast.AST, filepath: str) -> List[CodeSmell]:
        """Detect Long Parameter List smell"""
        smells = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                param_count = len(node.args.args)

                if param_count > self.config['long_parameter_list']['parameters']:
                    location = f"{filepath}:{node.lineno}"
                    smells.append(CodeSmell(
                        'Long Parameter List', 'warning', location,
                        {'parameters': param_count, 'threshold': self.config['long_parameter_list']['parameters']}
                    ))

        return smells

    def generate_report(self, smells: List[CodeSmell]) -> str:
        """Generate a human-readable report"""
        if not smells:
            return "No code smells detected!"

        # Group by severity
        by_severity = defaultdict(list)
        by_type = defaultdict(list)

        for smell in smells:
            by_severity[smell.severity].append(smell)
            by_type[smell.name].append(smell)

        report = ["=" * 60]
        report.append("CODE SMELL DETECTION REPORT")
        report.append("=" * 60)

        # Summary
        report.append(f"\nTotal Issues: {len(smells)}")
        for severity in ['error', 'warning', 'info']:
            count = len(by_severity[severity])
            if count:
                report.append(f"  {severity.upper()}: {count}")

        # By type
        report.append("\nIssues by Type:")
        for smell_type, type_smells in sorted(by_type.items()):
            report.append(f"  {smell_type}: {len(type_smells)}")

        # Detailed findings
        report.append("\n" + "=" * 60)
        report.append("DETAILED FINDINGS")
        report.append("=" * 60)

        for smell in sorted(smells, key=lambda s: s.severity, reverse=True):
            report.append(f"\n[{smell.severity.upper()}] {smell.name}")
            report.append(f"  Location: {smell.location}")
            report.append(f"  Details: {smell.details}")

        return "\n".join(report)


# Example usage
if __name__ == "__main__":
    detector = CodeSmellDetector()
    smells = detector.analyze_file("example.py")
    print(detector.generate_report(smells))
```

---

## References

### Primary Sources

1. **Fowler, M., Beck, K., Brant, J., Opdyke, W., & Roberts, D. (1999).**
   *Refactoring: Improving the Design of Existing Code.*
   Addison-Wesley. ISBN: 978-0201485677
   - Original catalog of 22 code smells
   - Refactoring techniques

2. **Beck, K. (1999).**
   "Code Smells." WikiWikiWeb.
   - Origin of the term "code smell"

3. **Refactoring.Guru. (2024).**
   "Code Smells."
   https://refactoring.guru/refactoring/smells
   - Comprehensive catalog with categories

4. **SourceMaking.com. (2024).**
   "Refactoring."
   https://sourcemaking.com/refactoring
   - Additional refactoring techniques

### Academic Research

5. **Tufano, M., Palomba, F., Bavota, G., Oliveto, R., Di Penta, M., De Lucia, A., & Poshyvanyk, D. (2015).**
   "When and Why Your Code Starts to Smell Bad."
   *IEEE/ACM 37th International Conference on Software Engineering (ICSE)*
   - Empirical study on code smell emergence
   - Analysis of 500,000+ commits

6. **McCabe, T. J. (1976).**
   "A Complexity Measure."
   *IEEE Transactions on Software Engineering*, SE-2(4), 308-320
   - Cyclomatic complexity definition

7. **Halstead, M. H. (1977).**
   *Elements of Software Science.*
   Elsevier North-Holland. ISBN: 0444002057
   - Halstead complexity measures

8. **Suryanarayana, G., Samarthyam, G., & Sharma, T. (2014).**
   *Refactoring for Software Design Smells: Managing Technical Debt.*
   Morgan Kaufmann. ISBN: 978-0128013977
   - Comprehensive catalog of design smells

9. **Sharma, T., & Spinellis, D. (2018).**
   "A Survey on Software Smells."
   *Journal of Systems and Software*, 138, 158-173
   - Systematic literature review

10. **Lanza, M., & Marinescu, R. (2006).**
    *Object-Oriented Metrics in Practice.*
    Springer. ISBN: 978-3540298033
    - Metrics for code smell detection

### Detection Techniques

11. **Spinellis, D. (2006).**
    "The Bad Code Spotter's Guide."
    *InformIT.*
    - Code smell detection strategies

12. **Kamiya, T., Kusumoto, S., & Inoue, K. (2002).**
    "CCFinder: A Multilinguistic Token-Based Code Clone Detection System for Large Scale Source Code."
    *IEEE Transactions on Software Engineering*, 28(7), 654-670
    - Token-based clone detection

13. **Baxter, I. D., Yahin, A., Moura, L., Sant'Anna, M., & Bier, L. (1998).**
    "Clone Detection Using Abstract Syntax Trees."
    *International Conference on Software Maintenance*
    - AST-based detection

### Tools and Standards

14. **SonarSource. (2024).**
    "SonarQube Code Quality Rules."
    https://www.sonarsource.com/
    - Industry-standard code quality rules

15. **NIST. (1996).**
    "Structured Testing: A Testing Methodology Using the Cyclomatic Complexity Metric."
    Special Publication 500-235
    - Complexity testing guidelines

16. **ISO/IEC.**
    *ISO/IEC 25010:2011 - Systems and Software Quality Requirements and Evaluation (SQuaRE).*
    - Maintainability standards

### Online Resources

17. **Wikipedia. (2024).**
    "Code Smell."
    https://en.wikipedia.org/wiki/Code_smell
    - General overview

18. **Wikipedia. (2024).**
    "Duplicate Code."
    https://en.wikipedia.org/wiki/Duplicate_code
    - Duplication detection methods

19. **Clean Code Developer Initiative.**
    "Clean Code Principles."
    - Best practices for code quality

20. **Robert C. Martin (Uncle Bob).**
    *Clean Code: A Handbook of Agile Software Craftsmanship.*
    Prentice Hall. 2008. ISBN: 978-0132350884
    - Principles and heuristics

---

## Appendix: Quick Reference

### Code Smell Detection Cheat Sheet

| Code Smell | Key Metric | Threshold | Detection Method |
|-------------|-------------|------------|-------------------|
| Long Method | LOC / Complexity | >50 lines, >10 CC | Direct count |
| God Class | Methods / Fields / WMC | >20 methods, >30 fields, WMC>100 | Multiple metrics |
| Duplicate Code | Similarity | >0.85 | Token/AST comparison |
| Feature Envy | Foreign Data Ratio | >50% | Access pattern analysis |
| Data Clumps | Co-occurrence | >3 times together | Frequent pattern mining |
| Long Parameter List | Parameter Count | >4-7 | Direct count |
| Shotgun Surgery | Change Impact | >4 classes affected | Change analysis |
| Divergent Change | Change Entropy | >2-3 categories | Change categorization |
| Dead Code | Reachability | Never called | Call graph analysis |
| Complex Method | Cyclomatic Complexity | >10 CC | Complexity calculation |
| Magic Numbers | Frequency | >2 occurrences | Pattern matching |
| Inappropriate Intimacy | Coupling | Fan-out >10 | Dependency analysis |

### Refactoring Techniques Summary

| Code Smell | Primary Refactoring Techniques |
|-------------|-----------------------------|
| Long Method | Extract Method, Replace Temp with Query |
| God Class | Extract Class, Extract Superclass, Decompose Conditional |
| Duplicate Code | Extract Method, Pull Up Method |
| Feature Envy | Move Method |
| Data Clumps | Introduce Parameter Object, Preserve Whole Object |
| Long Parameter List | Introduce Parameter Object, Remove Parameter |
| Shotgun Surgery | Move Method, Move Field, Inline Class |
| Divergent Change | Extract Class, Split Class |
| Dead Code | Remove Dead Code |
| Complex Method | Extract Method, Decompose Conditional |
| Magic Numbers | Replace Magic Number with Constant |
| Inappropriate Intimacy | Hide Delegate, Move Method |

### Metric Formulas Quick Reference

```
Cyclomatic Complexity:
  M = E - N + 2P

Halstead Volume:
  V = N × log₂(η₁ + η₂)

Halstead Difficulty:
  D = (η₁/2) × (N₂/η₂)

Gini Coefficient:
  G = ΣᵢΣⱼ|xᵢ - xⱼ| / (2n²μ)

IQR Upper Threshold:
  Upper = Q3 + 1.5 × (Q3 - Q1)

Z-Score:
  Z = (x - μ) / σ

Feature Envy Ratio:
  EDAR = Foreign_Accesses / Total_Accesses

Cohesion (TCC):
  TCC = Connected_Method_Pairs / Total_Method_Pairs
```

---

**Document Version:** 1.0
**Last Updated:** February 2026
**Authors:** Research Compilation based on cited sources

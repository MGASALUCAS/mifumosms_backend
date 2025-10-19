# Frontend Testing Guide - Mifumo SMS Integration

## 📋 Table of Contents
1. [Testing Environment Setup](#testing-environment-setup)
2. [API Testing Checklist](#api-testing-checklist)
3. [User Flow Testing](#user-flow-testing)
4. [Error Handling Testing](#error-handling-testing)
5. [Performance Testing](#performance-testing)
6. [Mobile Testing](#mobile-testing)
7. [Integration Testing](#integration-testing)
8. [Test Data Setup](#test-data-setup)

---

## 🧪 Testing Environment Setup

### 1. Development Environment
```bash
# Clone the repository
git clone https://github.com/your-org/mifumo-frontend.git
cd mifumo-frontend

# Install dependencies
npm install

# Set up environment variables
cp .env.example .env.local
```

### 2. Environment Variables
```env
# .env.local
REACT_APP_API_URL=http://localhost:8000/api
REACT_APP_WS_URL=ws://localhost:8000/ws
REACT_APP_DEBUG=true
```

### 3. Test User Accounts
Create test accounts with different roles and permissions:

```javascript
// Test users for different scenarios
const testUsers = {
  admin: {
    email: 'admin@test.com',
    password: 'Test123!',
    role: 'admin'
  },
  user: {
    email: 'user@test.com',
    password: 'Test123!',
    role: 'user'
  },
  limited: {
    email: 'limited@test.com',
    password: 'Test123!',
    role: 'limited'
  }
};
```

---

## ✅ API Testing Checklist

### Authentication Testing
- [ ] **Login with valid credentials**
  ```javascript
  // Test: Successful login
  const response = await sdk.login('user@test.com', 'Test123!');
  expect(response.success).toBe(true);
  expect(response.access).toBeDefined();
  ```

- [ ] **Login with invalid credentials**
  ```javascript
  // Test: Invalid credentials
  try {
    await sdk.login('user@test.com', 'wrongpassword');
  } catch (error) {
    expect(error.message).toContain('Invalid credentials');
  }
  ```

- [ ] **Token refresh**
  ```javascript
  // Test: Token refresh
  const refreshResponse = await sdk.refreshAccessToken();
  expect(refreshResponse.access).toBeDefined();
  ```

- [ ] **Logout**
  ```javascript
  // Test: Logout
  await sdk.logout();
  expect(sdk.accessToken).toBeNull();
  ```

### SMS Packages Testing
- [ ] **Get all packages**
  ```javascript
  // Test: Get packages
  const packages = await sdk.getSMSPackages();
  expect(packages.success).toBe(true);
  expect(packages.results).toHaveLength(5); // 5 packages available
  ```

- [ ] **Package data validation**
  ```javascript
  // Test: Package structure
  const package = packages.results[0];
  expect(package).toHaveProperty('id');
  expect(package).toHaveProperty('name');
  expect(package).toHaveProperty('credits');
  expect(package).toHaveProperty('price');
  expect(package).toHaveProperty('unit_price');
  ```

### SMS Balance Testing
- [ ] **Get current balance**
  ```javascript
  // Test: Get balance
  const balance = await sdk.getSMSBalance();
  expect(balance.success).toBe(true);
  expect(balance.data.credits).toBeGreaterThanOrEqual(0);
  ```

- [ ] **Balance updates after SMS sending**
  ```javascript
  // Test: Balance decreases after SMS
  const initialBalance = await sdk.getSMSBalance();
  await sdk.sendSMS('+255123456789', 'Test message', 'MIFUMO');
  const newBalance = await sdk.getSMSBalance();
  expect(newBalance.data.credits).toBeLessThan(initialBalance.data.credits);
  ```

### Payment Testing
- [ ] **Get payment providers**
  ```javascript
  // Test: Get providers
  const providers = await sdk.getPaymentProviders();
  expect(providers.success).toBe(true);
  expect(providers.providers).toHaveLength(4); // 4 providers available
  ```

- [ ] **Initiate package purchase**
  ```javascript
  // Test: Purchase package
  const purchase = await sdk.purchasePackage('package-id', 'vodacom');
  expect(purchase.success).toBe(true);
  expect(purchase.data.order_id).toBeDefined();
  ```

- [ ] **Custom SMS pricing**
  ```javascript
  // Test: Calculate custom pricing
  const pricing = await sdk.calculateCustomPricing(1000);
  expect(pricing.success).toBe(true);
  expect(pricing.data.total_price).toBeGreaterThan(0);
  ```

### SMS Sending Testing
- [ ] **Send single SMS**
  ```javascript
  // Test: Send SMS
  const sms = await sdk.sendSMS('+255123456789', 'Test message', 'MIFUMO');
  expect(sms.success).toBe(true);
  expect(sms.data.message_id).toBeDefined();
  ```

- [ ] **Send bulk SMS**
  ```javascript
  // Test: Send bulk SMS
  const recipients = ['+255123456789', '+255987654321'];
  const sms = await sdk.sendSMS(recipients, 'Bulk message', 'MIFUMO');
  expect(sms.success).toBe(true);
  expect(sms.data.recipients_count).toBe(2);
  ```

- [ ] **SMS with invalid phone number**
  ```javascript
  // Test: Invalid phone number
  try {
    await sdk.sendSMS('invalid-phone', 'Test message', 'MIFUMO');
  } catch (error) {
    expect(error.message).toContain('Invalid phone number');
  }
  ```

---

## 🔄 User Flow Testing

### 1. Complete Purchase Flow
```javascript
// Test: Complete purchase flow
async function testPurchaseFlow() {
  // 1. Login
  await sdk.login('user@test.com', 'Test123!');
  
  // 2. Get packages
  const packages = await sdk.getSMSPackages();
  const package = packages.results.find(p => p.is_popular);
  
  // 3. Get payment providers
  const providers = await sdk.getPaymentProviders();
  const provider = providers.providers[0];
  
  // 4. Initiate purchase
  const purchase = await sdk.purchasePackage(package.id, provider.code);
  
  // 5. Check payment status
  const status = await sdk.checkPaymentStatus(purchase.data.order_id);
  expect(status.success).toBe(true);
  
  // 6. Verify balance update (if payment completed)
  if (status.data.status === 'completed') {
    const balance = await sdk.getSMSBalance();
    expect(balance.data.credits).toBeGreaterThan(0);
  }
}
```

### 2. SMS Sending Flow
```javascript
// Test: SMS sending flow
async function testSMSSendingFlow() {
  // 1. Check balance
  const balance = await sdk.getSMSBalance();
  if (balance.data.credits < 1) {
    throw new Error('Insufficient credits for testing');
  }
  
  // 2. Get sender IDs
  const senderIDs = await sdk.getSenderIDs();
  const senderID = senderIDs.results[0];
  
  // 3. Send SMS
  const sms = await sdk.sendSMS('+255123456789', 'Test message', senderID.sender_id);
  
  // 4. Check SMS history
  const history = await sdk.getSMSHistory();
  const sentSMS = history.results.find(h => h.id === sms.data.message_id);
  expect(sentSMS).toBeDefined();
  
  // 5. Verify balance decreased
  const newBalance = await sdk.getSMSBalance();
  expect(newBalance.data.credits).toBeLessThan(balance.data.credits);
}
```

### 3. Sender ID Request Flow
```javascript
// Test: Sender ID request flow
async function testSenderIDRequestFlow() {
  // 1. Request new sender ID
  const request = await sdk.requestSenderID(
    'TESTID',
    'Test Company',
    '+255123456789',
    'Testing purposes'
  );
  
  // 2. Check request status
  const status = await sdk.getSenderIDStatus(request.data.id);
  expect(status.success).toBe(true);
  
  // 3. Wait for approval (in real scenario)
  // This would be tested with admin approval
}
```

---

## ⚠️ Error Handling Testing

### 1. Network Error Handling
```javascript
// Test: Network errors
async function testNetworkErrors() {
  // Simulate network failure
  const originalFetch = window.fetch;
  window.fetch = jest.fn().mockRejectedValue(new Error('Network error'));
  
  try {
    await sdk.getSMSPackages();
  } catch (error) {
    expect(error.message).toContain('Network error');
  } finally {
    window.fetch = originalFetch;
  }
}
```

### 2. Authentication Error Handling
```javascript
// Test: Authentication errors
async function testAuthErrors() {
  // Test with expired token
  sdk.accessToken = 'expired-token';
  
  try {
    await sdk.getSMSPackages();
  } catch (error) {
    expect(error.message).toContain('Authentication failed');
  }
}
```

### 3. Validation Error Handling
```javascript
// Test: Validation errors
async function testValidationErrors() {
  // Test invalid SMS data
  try {
    await sdk.sendSMS('', 'Test message', 'MIFUMO');
  } catch (error) {
    expect(error.message).toContain('Validation failed');
  }
  
  // Test invalid purchase data
  try {
    await sdk.purchasePackage('invalid-id', 'invalid-provider');
  } catch (error) {
    expect(error.message).toContain('Validation failed');
  }
}
```

### 4. Insufficient Credits Error
```javascript
// Test: Insufficient credits
async function testInsufficientCredits() {
  // Mock balance to 0
  const mockBalance = { success: true, data: { credits: 0 } };
  jest.spyOn(sdk, 'getSMSBalance').mockResolvedValue(mockBalance);
  
  try {
    await sdk.sendSMS('+255123456789', 'Test message', 'MIFUMO');
  } catch (error) {
    expect(error.message).toContain('Insufficient credits');
  }
}
```

---

## 🚀 Performance Testing

### 1. API Response Time Testing
```javascript
// Test: API response times
async function testAPIPerformance() {
  const startTime = Date.now();
  await sdk.getSMSPackages();
  const endTime = Date.now();
  
  const responseTime = endTime - startTime;
  expect(responseTime).toBeLessThan(2000); // Should respond within 2 seconds
}
```

### 2. Large Data Handling
```javascript
// Test: Large data sets
async function testLargeDataHandling() {
  // Test pagination with large SMS history
  const history = await sdk.getSMSHistory({ page_size: 100 });
  expect(history.data.purchases.length).toBeLessThanOrEqual(100);
  
  // Test bulk SMS sending
  const recipients = Array.from({ length: 100 }, (_, i) => `+25512345678${i}`);
  const sms = await sdk.sendSMS(recipients, 'Bulk test message', 'MIFUMO');
  expect(sms.data.recipients_count).toBe(100);
}
```

### 3. Memory Usage Testing
```javascript
// Test: Memory usage
async function testMemoryUsage() {
  const initialMemory = performance.memory?.usedJSHeapSize || 0;
  
  // Perform multiple API calls
  for (let i = 0; i < 100; i++) {
    await sdk.getSMSPackages();
  }
  
  const finalMemory = performance.memory?.usedJSHeapSize || 0;
  const memoryIncrease = finalMemory - initialMemory;
  
  // Memory increase should be reasonable
  expect(memoryIncrease).toBeLessThan(10 * 1024 * 1024); // Less than 10MB
}
```

---

## 📱 Mobile Testing

### 1. Responsive Design Testing
```javascript
// Test: Responsive design
async function testResponsiveDesign() {
  // Test different screen sizes
  const screenSizes = [
    { width: 320, height: 568 }, // iPhone SE
    { width: 375, height: 667 }, // iPhone 8
    { width: 414, height: 896 }, // iPhone 11 Pro Max
    { width: 768, height: 1024 }, // iPad
    { width: 1024, height: 768 }  // Desktop
  ];
  
  for (const size of screenSizes) {
    // Set viewport size
    window.innerWidth = size.width;
    window.innerHeight = size.height;
    
    // Test component rendering
    const packages = await sdk.getSMSPackages();
    expect(packages.success).toBe(true);
  }
}
```

### 2. Touch Interaction Testing
```javascript
// Test: Touch interactions
async function testTouchInteractions() {
  // Test touch events on mobile
  const button = document.querySelector('.purchase-button');
  
  // Simulate touch events
  const touchStart = new TouchEvent('touchstart', {
    touches: [new Touch({ identifier: 1, target: button })]
  });
  
  const touchEnd = new TouchEvent('touchend', {
    touches: [new Touch({ identifier: 1, target: button })]
  });
  
  button.dispatchEvent(touchStart);
  button.dispatchEvent(touchEnd);
  
  // Verify action was triggered
  expect(button.classList.contains('pressed')).toBe(true);
}
```

---

## 🔗 Integration Testing

### 1. End-to-End User Journey
```javascript
// Test: Complete user journey
async function testCompleteUserJourney() {
  // 1. Register new user
  const registration = await sdk.register({
    email: 'newuser@test.com',
    password: 'Test123!',
    first_name: 'New',
    last_name: 'User'
  });
  
  // 2. Login
  await sdk.login('newuser@test.com', 'Test123!');
  
  // 3. Get packages
  const packages = await sdk.getSMSPackages();
  
  // 4. Purchase package
  const purchase = await sdk.purchasePackage(packages.results[0].id, 'vodacom');
  
  // 5. Send SMS
  const sms = await sdk.sendSMS('+255123456789', 'Test message', 'MIFUMO');
  
  // 6. Check history
  const history = await sdk.getSMSHistory();
  expect(history.results.length).toBeGreaterThan(0);
}
```

### 2. Real-time Updates Testing
```javascript
// Test: Real-time updates
async function testRealTimeUpdates() {
  // Start balance polling
  const balanceUpdates = [];
  const stopPolling = sdk.pollBalance((balance) => {
    balanceUpdates.push(balance);
  });
  
  // Send SMS to trigger balance update
  await sdk.sendSMS('+255123456789', 'Test message', 'MIFUMO');
  
  // Wait for balance update
  await new Promise(resolve => setTimeout(resolve, 5000));
  
  // Stop polling
  stopPolling();
  
  // Verify balance was updated
  expect(balanceUpdates.length).toBeGreaterThan(0);
}
```

---

## 📊 Test Data Setup

### 1. Test Database Setup
```javascript
// Test: Database setup
async function setupTestData() {
  // Create test tenant
  const tenant = await sdk.updateTenantProfile({
    name: 'Test Company',
    business_name: 'Test Business',
    phone: '+255123456789',
    address: 'Test Address'
  });
  
  // Add test SMS balance
  // This would typically be done through admin interface
  // or test data seeding
  
  // Create test sender ID
  const senderID = await sdk.requestSenderID(
    'TESTID',
    'Test Company',
    '+255123456789'
  );
  
  return { tenant, senderID };
}
```

### 2. Test Cleanup
```javascript
// Test: Cleanup after tests
async function cleanupTestData() {
  // Remove test data
  try {
    await sdk.deleteSenderID('test-sender-id');
  } catch (error) {
    // Ignore if already deleted
  }
  
  // Clear tokens
  sdk.clearTokens();
}
```

---

## 🧪 Automated Testing Setup

### 1. Jest Configuration
```javascript
// jest.config.js
module.exports = {
  testEnvironment: 'jsdom',
  setupFilesAfterEnv: ['<rootDir>/src/setupTests.js'],
  testMatch: [
    '<rootDir>/src/**/__tests__/**/*.{js,jsx,ts,tsx}',
    '<rootDir>/src/**/*.{test,spec}.{js,jsx,ts,tsx}'
  ],
  collectCoverageFrom: [
    'src/**/*.{js,jsx,ts,tsx}',
    '!src/**/*.d.ts',
    '!src/index.js'
  ],
  coverageThreshold: {
    global: {
      branches: 80,
      functions: 80,
      lines: 80,
      statements: 80
    }
  }
};
```

### 2. Test Setup File
```javascript
// src/setupTests.js
import '@testing-library/jest-dom';
import { configure } from '@testing-library/react';

// Configure testing library
configure({ testIdAttribute: 'data-testid' });

// Mock fetch globally
global.fetch = jest.fn();

// Mock localStorage
const localStorageMock = {
  getItem: jest.fn(),
  setItem: jest.fn(),
  removeItem: jest.fn(),
  clear: jest.fn(),
};
global.localStorage = localStorageMock;
```

### 3. Test Utilities
```javascript
// src/test-utils.js
import { render } from '@testing-library/react';
import { MifumoProvider } from './context/MifumoContext';

const renderWithProvider = (ui, options = {}) => {
  const { sdk, ...renderOptions } = options;
  
  const Wrapper = ({ children }) => (
    <MifumoProvider sdk={sdk}>
      {children}
    </MifumoProvider>
  );
  
  return render(ui, { wrapper: Wrapper, ...renderOptions });
};

export * from '@testing-library/react';
export { renderWithProvider };
```

---

## 📈 Test Reporting

### 1. Coverage Reports
```bash
# Generate coverage report
npm run test -- --coverage

# Generate HTML coverage report
npm run test -- --coverage --coverageReporters=html
```

### 2. Test Results
```bash
# Run tests with verbose output
npm run test -- --verbose

# Run tests in watch mode
npm run test -- --watch

# Run specific test file
npm run test -- SMSBalance.test.js
```

---

## 🚀 Continuous Integration

### 1. GitHub Actions
```yaml
# .github/workflows/test.yml
name: Frontend Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Setup Node.js
      uses: actions/setup-node@v2
      with:
        node-version: '18'
        
    - name: Install dependencies
      run: npm ci
      
    - name: Run tests
      run: npm run test -- --coverage --watchAll=false
      
    - name: Upload coverage
      uses: codecov/codecov-action@v2
```

---

## 📝 Test Documentation

### 1. Test Plan Template
```markdown
## Test Plan: [Feature Name]

### Test Objectives
- [ ] Verify feature functionality
- [ ] Test error handling
- [ ] Validate performance
- [ ] Check mobile compatibility

### Test Cases
1. **Happy Path**
   - [ ] Test case 1
   - [ ] Test case 2
   
2. **Error Scenarios**
   - [ ] Test case 1
   - [ ] Test case 2
   
3. **Edge Cases**
   - [ ] Test case 1
   - [ ] Test case 2

### Test Data
- Test users: [List]
- Test data: [Description]
- Mock services: [List]

### Pass/Fail Criteria
- All test cases must pass
- Coverage must be > 80%
- Performance requirements met
```

---

*Last updated: January 2024*

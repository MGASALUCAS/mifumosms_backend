# Billing API Test Suite

This comprehensive test suite validates the Mifumo SMS Billing API implementation against the documentation and ensures all functionality works correctly with real data.

## 🎯 Test Coverage

### Unit Tests
- **SMSPackageAPITests** - SMS package listing, serialization, and validation
- **SMSBalanceAPITests** - SMS balance retrieval and tenant isolation
- **UsageStatisticsAPITests** - Usage statistics with filtering and aggregation
- **PurchaseAPITests** - Purchase history, details, and filtering
- **PaymentAPITests** - Payment initiation, tracking, and verification
- **CustomSMSAPITests** - Custom SMS pricing and purchase workflows
- **SubscriptionAPITests** - Subscription management and billing overview
- **AuthenticationTests** - Authentication and authorization requirements
- **ErrorHandlingTests** - Error scenarios and validation
- **DataValidationTests** - Data consistency and calculations

### Integration Tests
- **CompletePaymentFlowTests** - End-to-end payment workflows
- **DataConsistencyTests** - Cross-endpoint data consistency validation

## 🚀 Quick Start

### 1. Setup Test Data
```bash
python billing/setup_test_data.py
```

### 2. Run All Tests
```bash
python test_billing_api.py
```

### 3. Run Specific Test Types
```bash
# Unit tests only
python test_billing_api.py --unit

# Integration tests only
python test_billing_api.py --integration

# API validation tests only
python test_billing_api.py --validation

# With coverage report
python test_billing_api.py --coverage

# Verbose output
python test_billing_api.py --verbose
```

### 4. Run Specific Tests
```bash
# Run specific test class
python test_billing_api.py --test billing.tests.SMSPackageAPITests

# Run specific test method
python test_billing_api.py --test billing.tests.SMSPackageAPITests.test_list_sms_packages
```

## 📋 Tested Endpoints

### SMS Billing
- `GET /api/billing/sms/packages/` - List SMS packages
- `GET /api/billing/sms/balance/` - Get SMS balance
- `GET /api/billing/sms/usage/statistics/` - Get usage statistics
- `GET /api/billing/sms/purchases/` - List purchases
- `GET /api/billing/sms/purchases/{id}/` - Get purchase detail
- `GET /api/billing/sms/purchases/history/` - Get purchase history

### Payment Management
- `POST /api/billing/payments/initiate/` - Initiate payment
- `GET /api/billing/payments/verify/{order_id}/` - Verify payment
- `GET /api/billing/payments/active/` - Get active payments
- `GET /api/billing/payments/transactions/{id}/progress/` - Track payment progress
- `POST /api/billing/payments/transactions/{id}/cancel/` - Cancel payment
- `GET /api/billing/payments/providers/` - Get mobile money providers
- `GET /api/billing/payments/transactions/` - List payment transactions

### Custom SMS Purchase
- `POST /api/billing/payments/custom-sms/calculate/` - Calculate custom pricing
- `POST /api/billing/payments/custom-sms/initiate/` - Initiate custom purchase
- `GET /api/billing/payments/custom-sms/{id}/status/` - Check custom purchase status

### Subscription Management
- `GET /api/billing/plans/` - List billing plans
- `GET /api/billing/subscription/` - Get subscription details
- `GET /api/billing/overview/` - Get billing overview

## 🔍 What the Tests Validate

### API Response Format
- ✅ Response structure matches documentation
- ✅ Required fields are present
- ✅ Data types are correct
- ✅ Error responses follow documented format

### Business Logic
- ✅ SMS package pricing calculations
- ✅ Savings percentage calculations
- ✅ Sender ID validation
- ✅ Usage statistics aggregation
- ✅ Tenant isolation

### Payment Processing
- ✅ Payment initiation with ZenoPay
- ✅ Mobile money provider validation
- ✅ Phone number format validation
- ✅ Payment status tracking
- ✅ Payment cancellation

### Data Consistency
- ✅ Cross-endpoint data consistency
- ✅ Balance calculations
- ✅ Purchase history accuracy
- ✅ Usage statistics accuracy

### Error Handling
- ✅ Invalid input validation
- ✅ Authentication requirements
- ✅ Authorization checks
- ✅ Proper error messages

## 📊 Test Data

The test suite uses realistic data that matches the documentation examples:

### SMS Packages
- **Lite Package**: 1000 credits, TZS 25,000 (TZS 25 per SMS)
- **Standard Package**: 5000 credits, TZS 100,000 (TZS 20 per SMS) - Popular
- **Pro Package**: 10000 credits, TZS 150,000 (TZS 15 per SMS)
- **Enterprise Package**: 50000 credits, TZS 500,000 (TZS 10 per SMS)

### Mobile Money Providers
- **Vodacom M-Pesa** (vodacom)
- **Tigo Pesa** (tigo)
- **Airtel Money** (airtel)
- **Halotel Money** (halotel)

### Test Scenarios
- Complete payment workflows
- Custom SMS purchase flows
- Subscription management
- Usage statistics with various filters
- Error handling scenarios
- Data consistency validation

## 🛠️ Test Configuration

### Database
Tests use SQLite in-memory database for fast execution and isolation.

### Authentication
Tests use JWT tokens with test users and tenants.

### Mocking
ZenoPay API calls are mocked to avoid external dependencies during testing.

## 📈 Coverage Report

Run tests with coverage to see detailed coverage information:

```bash
python test_billing_api.py --coverage
```

This generates:
- Console coverage report
- HTML coverage report in `htmlcov/` directory

## 🔧 Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Make sure you're in the project root directory
   cd /path/to/mifumosms_backend
   python test_billing_api.py
   ```

2. **Database Errors**
   ```bash
   # Run migrations first
   python manage.py migrate
   ```

3. **Missing Dependencies**
   ```bash
   # Install test dependencies
   pip install coverage
   ```

### Debug Mode

Run tests with verbose output to see detailed information:

```bash
python test_billing_api.py --verbose
```

## 📝 Test Report

After running tests, a comprehensive report is generated:

```bash
python test_billing_api.py --report
```

This creates `BILLING_API_TEST_REPORT.md` with:
- Test coverage summary
- Endpoint validation results
- Recommendations
- Next steps

## 🎉 Success Criteria

All tests must pass for the billing API to be considered ready:

- ✅ All unit tests pass
- ✅ All integration tests pass
- ✅ All API validation tests pass
- ✅ Response formats match documentation
- ✅ Error handling works correctly
- ✅ Data consistency maintained
- ✅ Authentication and authorization work
- ✅ Mobile money integration ready

## 🚀 Next Steps

After all tests pass:

1. **Deploy to staging** for user acceptance testing
2. **Set up monitoring** for production deployment
3. **Create API documentation** for frontend team
4. **Plan production deployment** with rollback strategy
5. **Set up automated testing** in CI/CD pipeline

## 📞 Support

For questions about the test suite:

- Check the test output for specific error messages
- Review the test code for implementation details
- Run individual tests to isolate issues
- Use verbose mode for detailed debugging information

---

**Happy Testing! 🧪✨**

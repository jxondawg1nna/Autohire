# Autohire Analytics & Monitoring System - Setup Guide

## Overview

This guide provides comprehensive setup instructions for the Autohire Analytics and Monitoring System. The system includes:

- **Business Analytics Dashboard**: Real-time KPIs, user engagement, and job market analytics
- **System Performance Monitoring**: API response times, error rates, and system health
- **User Experience Analytics**: Page load times, user journeys, and feature usage
- **Security & Compliance Monitoring**: Authentication events, data access patterns
- **Revenue & Business Intelligence**: Subscription metrics, ROI measurement
- **Automated Reporting**: Scheduled reports and data export capabilities

## System Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   Database      │
│   Dashboard     │◄──►│   Analytics     │◄──►│   PostgreSQL    │
│   (Next.js)     │    │   APIs          │    │   + Extensions  │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Data Pipeline │
                       │   - Collection  │
                       │   - Processing  │
                       │   - Aggregation │
                       └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Monitoring    │
                       │   & Alerting    │
                       │   System        │
                       └─────────────────┘
```

## Prerequisites

### Software Requirements
- Python 3.9+
- Node.js 18+
- PostgreSQL 14+
- Redis 6+
- Docker (optional, for containerized deployment)

### Python Dependencies
```bash
pip install fastapi sqlalchemy asyncpg redis celery
pip install pandas numpy matplotlib seaborn
pip install pdfkit jinja2 openpyxl
pip install psutil aiohttp
```

### Node.js Dependencies
```bash
npm install @tanstack/react-query framer-motion
npm install recharts date-fns clsx
npm install lucide-react @heroicons/react
```

## Installation Steps

### 1. Database Setup

Run the analytics enhancement migration:

```bash
cd backend
alembic upgrade head
```

This creates the following new tables:
- `monitoring_alerts`
- `system_health_snapshots`
- `data_quality_reports`
- `application_performance_logs`
- `job_application_funnel`
- `user_segmentation`
- `feature_usage_analytics`

### 2. Environment Configuration

Add to your `.env` file:

```env
# Analytics Configuration
ANALYTICS_RETENTION_DAYS=365
ENABLE_MESSAGE_TRACKING=true
ENABLE_CLICK_TRACKING=true
ENABLE_OPEN_TRACKING=true

# Monitoring Configuration
MONITORING_ENABLED=true
ALERT_EMAIL_RECIPIENTS=admin@autohire.com,ops@autohire.com
SLACK_WEBHOOK_URL=https://hooks.slack.com/services/YOUR/SLACK/WEBHOOK

# Reporting Configuration
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SMTP_USE_TLS=true

# Performance Thresholds
CPU_WARNING_THRESHOLD=70
CPU_CRITICAL_THRESHOLD=85
MEMORY_WARNING_THRESHOLD=80
MEMORY_CRITICAL_THRESHOLD=90
API_RESPONSE_WARNING_MS=1000
API_RESPONSE_CRITICAL_MS=2000
```

### 3. Backend Integration

Update your main FastAPI application to include analytics routes:

```python
# backend/main.py
from app.api import analytics, monitoring
from app.services.data_pipeline import pipeline_orchestrator
from app.services.monitoring_service import monitoring_service
from app.services.reporting_service import reporting_service

# Add routers
app.include_router(analytics.router)
app.include_router(monitoring.router)

@app.on_event("startup")
async def startup_event():
    """Start analytics and monitoring services"""
    import asyncio
    
    # Start data pipeline
    asyncio.create_task(pipeline_orchestrator.start())
    
    # Start monitoring service
    asyncio.create_task(monitoring_service.start_monitoring())
    
    # Start reporting scheduler
    asyncio.create_task(reporting_service.start_scheduler())

@app.on_event("shutdown")
async def shutdown_event():
    """Stop analytics and monitoring services"""
    await pipeline_orchestrator.stop()
    await monitoring_service.stop_monitoring()
    await reporting_service.stop_scheduler()
```

### 4. Frontend Integration

Add the analytics dashboard to your Next.js application:

```typescript
// app/analytics/page.tsx
import { AnalyticsDashboard } from '@/components/analytics/AnalyticsDashboard';

export default function AnalyticsPage() {
  return (
    <div className="container mx-auto py-8">
      <AnalyticsDashboard />
    </div>
  );
}
```

Update your navigation to include analytics:

```typescript
// components/navigation.tsx
const navigationItems = [
  // ... existing items
  {
    name: 'Analytics',
    href: '/analytics',
    icon: ChartBarIcon,
  },
];
```

### 5. Event Tracking Integration

Add event tracking throughout your application:

```typescript
// utils/analytics.ts
import { analyticsApi } from '@/lib/api/analytics';

export const trackEvent = async (
  eventType: string,
  eventName: string,
  properties?: Record<string, any>
) => {
  try {
    await analyticsApi.trackEvent({
      event_type: eventType,
      event_name: eventName,
      properties: properties || {},
      metadata: {
        timestamp: new Date().toISOString(),
        user_agent: navigator.userAgent,
        url: window.location.href,
      },
    });
  } catch (error) {
    console.error('Failed to track event:', error);
  }
};

// Usage examples:
// trackEvent('user_action', 'job_view', { job_id: '123', category: 'engineering' });
// trackEvent('user_action', 'job_apply', { job_id: '123', method: 'automated' });
// trackEvent('navigation', 'page_view', { page: '/dashboard' });
```

### 6. API Middleware for Performance Tracking

Add performance tracking middleware:

```python
# backend/app/middleware/analytics.py
import time
from fastapi import Request, Response
from app.services.analytics_service import analytics_service

async def analytics_middleware(request: Request, call_next):
    start_time = time.time()
    
    # Process request
    response = await call_next(request)
    
    # Calculate response time
    process_time = (time.time() - start_time) * 1000
    
    # Track API performance
    await analytics_service.track_event(
        event_type="api_request",
        event_name=f"{request.method}_{request.url.path}",
        properties={
            "method": request.method,
            "path": str(request.url.path),
            "status_code": response.status_code,
            "response_time_ms": process_time,
        },
        metadata={
            "ip_address": request.client.host,
            "user_agent": request.headers.get("user-agent"),
        }
    )
    
    return response

# Add to main.py
app.middleware("http")(analytics_middleware)
```

## Configuration Options

### Monitoring Thresholds

Customize monitoring thresholds in the monitoring service:

```python
# Custom monitor configuration
monitoring_service.add_scheduled_report(MonitorConfig(
    name="custom_business_metric",
    monitor_type=MonitorType.BUSINESS,
    metric_name="daily_revenue",
    check_interval=3600,  # 1 hour
    threshold_warning=1000.0,
    threshold_critical=500.0,
    comparison_operator="<",  # Alert when revenue is too low
    notification_channels=["email", "slack"]
))
```

### Custom Reports

Add custom scheduled reports:

```python
# Custom report configuration
reporting_service.add_scheduled_report(ReportConfig(
    name="custom_weekly_report",
    report_type=ReportType.WEEKLY_BUSINESS,
    frequency=ReportFrequency.WEEKLY,
    format=ReportFormat.PDF,
    recipients=["team@autohire.com"],
    parameters={
        "include_charts": True,
        "include_recommendations": True,
        "focus_areas": ["user_growth", "application_success"]
    }
))
```

### Data Export Configuration

Configure automated data exports:

```python
# Schedule daily data export
async def schedule_data_export():
    yesterday = datetime.utcnow() - timedelta(days=1)
    today = datetime.utcnow()
    
    export_data = await reporting_service.export_data(
        data_type="user_events",
        format=ReportFormat.CSV,
        start_date=yesterday,
        end_date=today
    )
    
    # Save to S3 or send via email
    # Implementation depends on your infrastructure
```

## Dashboard Customization

### Adding Custom Metrics

Create custom KPI cards:

```typescript
// components/analytics/CustomKPICard.tsx
<KPICard
  title="Custom Metric"
  value={customValue}
  change={customChange}
  icon={CustomIcon}
  color="blue"
  format="number"
  subtitle="Your custom description"
/>
```

### Custom Charts

Add custom visualization components:

```typescript
// components/analytics/CustomChart.tsx
export const CustomChart: React.FC<{ data: any }> = ({ data }) => {
  return (
    <ResponsiveContainer width="100%" height={300}>
      <LineChart data={data}>
        <CartesianGrid strokeDasharray="3 3" />
        <XAxis dataKey="date" />
        <YAxis />
        <Tooltip />
        <Line type="monotone" dataKey="value" stroke="#8884d8" />
      </LineChart>
    </ResponsiveContainer>
  );
};
```

## Security Considerations

### Data Privacy

1. **Personal Data Anonymization**: Ensure PII is anonymized in analytics
2. **GDPR Compliance**: Implement data retention policies
3. **Access Control**: Restrict analytics access based on user roles

```python
# Example: Anonymize user data
async def anonymize_user_data(user_id: str) -> str:
    # Hash user ID for analytics while maintaining uniqueness
    import hashlib
    return hashlib.sha256(f"user_{user_id}".encode()).hexdigest()[:16]
```

### API Security

1. **Rate Limiting**: Implement rate limits on analytics endpoints
2. **Authentication**: Ensure all analytics endpoints require authentication
3. **Input Validation**: Validate all analytics data inputs

## Performance Optimization

### Database Optimization

1. **Indexes**: Ensure proper indexing on analytics tables
2. **Partitioning**: Consider table partitioning for large datasets
3. **Archiving**: Implement data archiving for old analytics data

```sql
-- Example: Partition analytics_events table by date
CREATE TABLE analytics_events_2024_01 PARTITION OF analytics_events
FOR VALUES FROM ('2024-01-01') TO ('2024-02-01');
```

### Caching Strategy

1. **Redis Caching**: Cache frequently accessed analytics data
2. **CDN**: Use CDN for static analytics assets
3. **Query Optimization**: Optimize expensive analytics queries

```python
# Example: Cache analytics data
@cache_result(ttl=300)  # Cache for 5 minutes
async def get_cached_kpis():
    return await analytics_service.get_business_kpis()
```

## Monitoring and Alerting

### Alert Configuration

Set up critical alerts for system health:

1. **System Resources**: CPU, memory, disk usage
2. **Application Performance**: API response times, error rates
3. **Business Metrics**: User registration drops, application failures
4. **Security Events**: Failed login attempts, unusual access patterns

### Notification Channels

Configure multiple notification channels:

1. **Email**: For detailed reports and non-urgent alerts
2. **Slack**: For real-time team notifications
3. **SMS**: For critical system failures (using Twilio)
4. **Webhooks**: For integration with external monitoring tools

## Troubleshooting

### Common Issues

1. **High Memory Usage**: Analytics data processing can be memory-intensive
   - Solution: Implement data streaming and batch processing
   - Monitor: Set memory usage alerts

2. **Slow Dashboard Loading**: Large datasets can slow dashboard rendering
   - Solution: Implement data pagination and lazy loading
   - Optimize: Use aggregated data for overview metrics

3. **Missing Data**: Events not being tracked properly
   - Check: Analytics middleware configuration
   - Verify: Database connections and permissions

### Debug Mode

Enable debug mode for detailed logging:

```python
# Enable debug logging for analytics
import logging
logging.getLogger('app.services.analytics').setLevel(logging.DEBUG)
```

### Health Checks

Implement health check endpoints:

```python
@app.get("/health/analytics")
async def analytics_health_check():
    try:
        # Test database connection
        async with get_db_session() as db:
            await db.execute(text("SELECT 1"))
        
        # Test Redis connection
        redis_client.ping()
        
        return {"status": "healthy", "services": ["database", "redis"]}
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

## Production Deployment

### Environment-Specific Configuration

```yaml
# docker-compose.analytics.yml
version: '3.8'
services:
  analytics-worker:
    build: .
    command: python -m app.services.data_pipeline
    environment:
      - ANALYTICS_ENABLED=true
      - MONITORING_ENABLED=true
    depends_on:
      - postgres
      - redis

  monitoring-service:
    build: .
    command: python -m app.services.monitoring_service
    environment:
      - MONITORING_ENABLED=true
    depends_on:
      - postgres
      - redis
```

### Scaling Considerations

1. **Horizontal Scaling**: Use multiple worker processes for data processing
2. **Load Balancing**: Distribute analytics requests across multiple instances
3. **Database Sharding**: Consider sharding for very large datasets

## Maintenance

### Regular Tasks

1. **Data Cleanup**: Remove old analytics data based on retention policy
2. **Index Maintenance**: Rebuild indexes periodically
3. **Report Review**: Review and update scheduled reports
4. **Alert Tuning**: Adjust alert thresholds based on system behavior

### Backup Strategy

1. **Database Backups**: Regular backups of analytics data
2. **Configuration Backups**: Backup monitoring and reporting configurations
3. **Dashboard Exports**: Export dashboard configurations

## Support and Documentation

### Additional Resources

- [API Documentation](./api-docs.md)
- [Dashboard User Guide](./dashboard-guide.md)
- [Monitoring Setup](./monitoring-setup.md)
- [Troubleshooting Guide](./troubleshooting.md)

### Getting Help

For support with the analytics system:

1. Check the troubleshooting guide
2. Review application logs
3. Contact the development team
4. Submit issues via the project repository

---

**Note**: This analytics and monitoring system is designed to be comprehensive yet flexible. Customize the configuration based on your specific needs and infrastructure requirements.
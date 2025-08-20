# Real-Time Notifications API Documentation

## Overview
نظام الإشعارات في الوقت الفعلي يستخدم WebSocket للتواصل المباشر مع العملاء، بالإضافة إلى REST API endpoints للعمليات الأساسية.

## WebSocket Connection

### Connection URL
```
ws://localhost:8000/ws/notifications/
```

### Authentication
يجب إرسال JWT token مع الاتصال بإحدى الطرق التالية:

#### 1. Query Parameter
```javascript
const token = "your_jwt_access_token";
const ws = new WebSocket(`ws://localhost:8000/ws/notifications/?token=${token}`);
```

#### 2. Authorization Header
```javascript
const ws = new WebSocket("ws://localhost:8000/ws/notifications/", [], {
    headers: {
        'Authorization': `Bearer ${token}`
    }
});
```

### WebSocket Messages

#### Messages from Client to Server

##### 1. Mark Notification as Read
```json
{
    "type": "mark_as_read",
    "notification_id": 123
}
```

##### 2. Mark All Notifications as Read
```json
{
    "type": "mark_all_as_read"
}
```

##### 3. Get Unread Count
```json
{
    "type": "get_unread_count"
}
```

#### Messages from Server to Client

##### 1. Initial Notifications (عند الاتصال)
```json
{
    "type": "initial_notifications",
    "notifications": [
        {
            "id": 123,
            "sender": {
                "id": 456,
                "username": "john_doe",
                "profile_picture": "http://example.com/pic.jpg"
            },
            "notification_type": "like",
            "trip_title": "رحلة إلى باريس",
            "trip_image": "http://example.com/trip.jpg",
            "notification_message": "john_doe أعجب برحلتك",
            "time_ago": "منذ 5 دقائق",
            "is_read": false,
            "created_at": "2025-08-19T10:30:00Z"
        }
    ],
    "unread_count": 5
}
```

##### 2. New Notification
```json
{
    "type": "new_notification",
    "notification": {
        "id": 124,
        "sender": {
            "id": 789,
            "username": "jane_smith",
            "profile_picture": "http://example.com/jane.jpg"
        },
        "notification_type": "comment",
        "trip_title": "رحلة إلى دبي",
        "comment_content": "رحلة رائعة! أين هذا المكان بالضبط؟",
        "notification_message": "jane_smith علق على رحلتك",
        "time_ago": "الآن",
        "is_read": false,
        "created_at": "2025-08-19T11:00:00Z"
    }
}
```

##### 3. Unread Count Update
```json
{
    "type": "unread_count_update",
    "unread_count": 3
}
```

##### 4. Unread Count Response
```json
{
    "type": "unread_count",
    "unread_count": 7
}
```

## REST API Endpoints

### Base URL
```
http://localhost:8000/api/interactions/
```

### Authentication
جميع الـ endpoints تتطلب JWT authentication:
```
Authorization: Bearer your_jwt_access_token
```

### Endpoints

#### 1. Get Notifications List
```http
GET /notifications/
```

**Query Parameters:**
- `page` (optional): رقم الصفحة
- `page_size` (optional): عدد العناصر في الصفحة

**Response:**
```json
{
    "count": 50,
    "next": "http://localhost:8000/api/interactions/notifications/?page=2",
    "previous": null,
    "results": [
        {
            "id": 123,
            "sender": {...},
            "notification_type": "like",
            "trip_title": "رحلة إلى باريس",
            "notification_message": "john_doe أعجب برحلتك",
            "time_ago": "منذ 5 دقائق",
            "is_read": false,
            "created_at": "2025-08-19T10:30:00Z"
        }
    ]
}
```

#### 2. Get Unread Notifications Count
```http
GET /notifications/unread-count/
```

**Response:**
```json
{
    "unread_count": 5
}
```

#### 3. Get Recent Notifications
```http
GET /notifications/recent/
```

**Query Parameters:**
- `limit` (optional): عدد الإشعارات المطلوبة (افتراضي: 20)

**Response:**
```json
{
    "notifications": [...],
    "count": 15
}
```

#### 4. Mark Notification as Read (Real-time)
```http
POST /notifications/{notification_id}/read-realtime/
```

**Response:**
```json
{
    "message": "Notification marked as read"
}
```

#### 5. Mark All Notifications as Read
```http
POST /notifications/read-all/
```

**Response:**
```json
{
    "message": "3 notifications marked as read",
    "count": 3
}
```

#### 6. Delete Notification
```http
DELETE /notifications/{notification_id}/delete/
```

**Response:**
```json
{
    "message": "Notification deleted"
}
```

#### 7. Get Notification Settings
```http
GET /notifications/settings/
```

**Response:**
```json
{
    "likes_enabled": true,
    "comments_enabled": true,
    "follows_enabled": true,
    "shares_enabled": true,
    "email_notifications": false,
    "push_notifications": true
}
```

#### 8. Update Notification Settings
```http
POST /notifications/settings/update/
```

**Request Body:**
```json
{
    "likes_enabled": false,
    "comments_enabled": true,
    "email_notifications": true
}
```

**Response:**
```json
{
    "message": "Settings updated successfully"
}
```

## Notification Types

| Type | Description | Arabic |
|------|-------------|---------|
| `like` | إعجاب برحلة | أعجب برحلتك |
| `comment` | تعليق على رحلة | علق على رحلتك |
| `follow` | متابعة مستخدم | بدأ متابعتك |
| `share` | مشاركة رحلة | شارك رحلتك |

## Frontend Integration Example

### JavaScript WebSocket Client
```javascript
class NotificationManager {
    constructor(token) {
        this.token = token;
        this.ws = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 5;
    }

    connect() {
        this.ws = new WebSocket(`ws://localhost:8000/ws/notifications/?token=${this.token}`);
        
        this.ws.onopen = () => {
            console.log('Connected to notifications WebSocket');
            this.reconnectAttempts = 0;
        };

        this.ws.onmessage = (event) => {
            const data = JSON.parse(event.data);
            this.handleMessage(data);
        };

        this.ws.onclose = () => {
            console.log('Disconnected from notifications WebSocket');
            this.reconnect();
        };

        this.ws.onerror = (error) => {
            console.error('WebSocket error:', error);
        };
    }

    handleMessage(data) {
        switch(data.type) {
            case 'initial_notifications':
                this.updateNotificationsList(data.notifications);
                this.updateUnreadCount(data.unread_count);
                break;
            
            case 'new_notification':
                this.addNewNotification(data.notification);
                this.showNotificationToast(data.notification);
                break;
            
            case 'unread_count_update':
                this.updateUnreadCount(data.unread_count);
                break;
        }
    }

    markAsRead(notificationId) {
        this.ws.send(JSON.stringify({
            type: 'mark_as_read',
            notification_id: notificationId
        }));
    }

    markAllAsRead() {
        this.ws.send(JSON.stringify({
            type: 'mark_all_as_read'
        }));
    }

    reconnect() {
        if (this.reconnectAttempts < this.maxReconnectAttempts) {
            this.reconnectAttempts++;
            setTimeout(() => {
                console.log(`Reconnecting... Attempt ${this.reconnectAttempts}`);
                this.connect();
            }, 1000 * this.reconnectAttempts);
        }
    }
}

// Usage
const notificationManager = new NotificationManager(userToken);
notificationManager.connect();
```

## Error Handling

### WebSocket Errors
- **401 Unauthorized**: Invalid or expired token
- **Connection Lost**: Auto-reconnection with exponential backoff

### API Errors
- **400 Bad Request**: Invalid request data
- **401 Unauthorized**: Authentication required
- **404 Not Found**: Notification not found
- **500 Internal Server Error**: Server error

## Performance Considerations

1. **Connection Limits**: كل مستخدم يمكنه فتح اتصال WebSocket واحد فقط
2. **Message Rate Limiting**: محدود بـ 100 رسالة في الدقيقة لكل مستخدم
3. **Notification History**: يتم الاحتفاظ بآخر 1000 إشعار لكل مستخدم
4. **Auto-cleanup**: الإشعارات الأقدم من 30 يوم يتم حذفها تلقائياً

## Testing

### WebSocket Testing
```bash
# تشغيل الاختبارات
python manage.py test interactions.tests.NotificationUtilsTest
python manage.py test interactions.tests.NotificationSignalsTest
```

### API Testing
```bash
# اختبار الـ endpoints
python manage.py test interactions.tests.InteractionsEndpointsTest
```

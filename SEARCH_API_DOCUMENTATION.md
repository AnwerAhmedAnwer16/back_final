# Search API Documentation

## Overview
نظام البحث الشامل يوفر إمكانية البحث السريع في المستخدمين والتاجز مع دعم للفلترة والترتيب المحسن للنتائج.

## Base URL
```
http://localhost:8000/api/search/
```

## Authentication
جميع endpoints متاحة بدون authentication، لكن بعض البيانات الإضافية (مثل is_following) تظهر فقط للمستخدمين المسجلين.

---

## 🔍 Unified Search API

### Endpoint
```
GET /api/search/?q={search_term}
```

### Description
البحث الموحد في المستخدمين والتاجز معاً مع ترتيب النتائج حسب الشعبية.

### Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| q | string | Yes | كلمة البحث (2-100 حرف) |

### Request Example
```bash
GET /api/search/?q=ahmed
```

### Response Example
```json
{
    "query": "ahmed",
    "results": [
        {
            "type": "user",
            "id": 1,
            "username": "ahmed123",
            "profile_url": "http://localhost:8000/api/accounts/users/1/profile/",
            "followers_count": 150,
            "avatar": "http://localhost:8000/media/avatars/1/avatar.jpg",
            "full_name": "Ahmed Mohamed"
        },
        {
            "type": "tag",
            "name": "adventure",
            "trips_url": "http://localhost:8000/api/trip/tags/adventure/trips/",
            "trips_count": 25
        }
    ],
    "total_results": 2,
    "users_count": 1,
    "tags_count": 1
}
```

### Error Responses
```json
// Missing query parameter
{
    "error": "يرجى إدخال كلمة البحث",
    "error_code": "MISSING_QUERY"
}

// Query too short
{
    "error": "يجب أن تكون كلمة البحث أكثر من حرف واحد",
    "error_code": "QUERY_TOO_SHORT"
}

// Query too long
{
    "error": "كلمة البحث طويلة جداً",
    "error_code": "QUERY_TOO_LONG"
}

// Server error
{
    "error": "حدث خطأ أثناء البحث",
    "error_code": "SEARCH_ERROR"
}
```

---

## 👥 User Search API

### Endpoint
```
GET /api/search/users/?q={search_term}
```

### Description
البحث في المستخدمين فقط باستخدام username, first_name, last_name.

### Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| q | string | Yes | كلمة البحث (2+ أحرف) |
| page | integer | No | رقم الصفحة (default: 1) |
| page_size | integer | No | عدد النتائج في الصفحة (max: 50) |

### Request Example
```bash
GET /api/search/users/?q=ahmed&page=1&page_size=10
```

### Response Example
```json
{
    "count": 25,
    "next": "http://localhost:8000/api/search/users/?page=2&q=ahmed",
    "previous": null,
    "results": [
        {
            "id": 1,
            "username": "ahmed123",
            "profile": {
                "first_name": "Ahmed",
                "last_name": "Mohamed",
                "bio": "Travel enthusiast",
                "avatar": "http://localhost:8000/media/avatars/1/avatar.jpg",
                "country": "Egypt",
                "gender": "M"
            },
            "followers_count": 150
        },
        {
            "id": 2,
            "username": "ahmed_travel",
            "profile": {
                "first_name": "Ahmed",
                "last_name": "Ali",
                "bio": "",
                "avatar": null,
                "country": "UAE",
                "gender": "M"
            },
            "followers_count": 75
        }
    ]
}
```

---

## 🏷️ Tag Search API

### Endpoint
```
GET /api/search/tags/?q={search_term}
```

### Description
البحث في التاجز مع عرض عدد الرحلات لكل تاج.

### Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| q | string | Yes | كلمة البحث (2+ أحرف) |
| page | integer | No | رقم الصفحة (default: 1) |
| page_size | integer | No | عدد النتائج في الصفحة (max: 50) |

### Request Example
```bash
GET /api/search/tags/?q=adventure&page=1
```

### Response Example
```json
{
    "count": 5,
    "next": null,
    "previous": null,
    "results": [
        {
            "tripTag": "adventure",
            "trips_count": 25,
            "trips_url": "http://localhost:8000/api/trip/tags/adventure/trips/"
        },
        {
            "tripTag": "adventure_travel",
            "trips_count": 12,
            "trips_url": "http://localhost:8000/api/trip/tags/adventure_travel/trips/"
        }
    ]
}
```

---

## 👤 Public User Profile API

### Endpoint
```
GET /api/accounts/users/{user_id}/profile/
```

### Description
عرض البروفايل العام لأي مستخدم مع إحصائياته ومعلومات المتابعة.

### Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| user_id | integer | Yes | معرف المستخدم |

### Request Example
```bash
GET /api/accounts/users/1/profile/
```

### Response Example
```json
{
    "id": 1,
    "username": "ahmed123",
    "date_joined": "2024-01-15T10:30:00Z",
    "is_verified": true,
    "profile": {
        "first_name": "Ahmed",
        "last_name": "Mohamed",
        "bio": "Travel enthusiast and photographer",
        "avatar": "http://localhost:8000/media/avatars/1/avatar.jpg",
        "country": "Egypt",
        "gender": "M"
    },
    "followers_count": 150,
    "following_count": 89,
    "trips_count": 23,
    "is_following": false
}
```

### Error Response
```json
{
    "detail": "المستخدم غير موجود"
}
```

---

## 📍 Tag Trips API

### Endpoint
```
GET /api/trip/tags/{tag_name}/trips/
```

### Description
عرض جميع الرحلات التي تحتوي على تاج معين مع pagination.

### Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| tag_name | string | Yes | اسم التاج |
| page | integer | No | رقم الصفحة (default: 1) |
| page_size | integer | No | عدد النتائج في الصفحة (max: 100) |

### Request Example
```bash
GET /api/trip/tags/adventure/trips/?page=1&page_size=20
```

### Response Example
```json
{
    "count": 25,
    "next": "http://localhost:8000/api/trip/tags/adventure/trips/?page=2",
    "previous": null,
    "tag_info": {
        "tag_name": "adventure",
        "trips_count": 25
    },
    "results": [
        {
            "id": 1,
            "user": "ahmed123",
            "caption": "Amazing adventure in the mountains!",
            "location": "Swiss Alps",
            "created_at": "2024-08-15T14:30:00Z",
            "updated_at": "2024-08-15T14:30:00Z",
            "images": [
                {
                    "id": 1,
                    "image": "http://localhost:8000/media/trips/1/images/mountain.jpg"
                }
            ],
            "videos": [],
            "tags": [
                {
                    "id": 1,
                    "tripTag": "adventure"
                },
                {
                    "id": 2,
                    "tripTag": "mountains"
                }
            ]
        }
    ]
}
```

### Error Response
```json
{
    "error": "لا توجد رحلات بالتاج \"nonexistent\""
}
```

---

## 🚀 Performance Features

### Database Optimization
- **Indexes** على حقول البحث الرئيسية
- **select_related** و **prefetch_related** لتقليل عدد الاستعلامات
- **Pagination** لتحسين الأداء مع البيانات الكبيرة

### Search Features
- **Case-insensitive search** في جميع الحقول
- **Partial matching** باستخدام `icontains`
- **Sorting** حسب الشعبية (followers_count, trips_count)
- **Distinct results** لتجنب التكرار

### Error Handling
- **Validation** لطول كلمة البحث
- **Proper HTTP status codes**
- **Descriptive error messages** باللغة العربية
- **Error codes** للتعامل البرمجي

---

## 🚀 Real-time Search APIs

### Quick Search API (Type as you type)

#### Endpoint
```
GET /api/search/quick/?q={search_term}
```

#### Description
بحث سريع محسن للكتابة المباشرة مع نتائج فورية ومحدودة.

#### Features
- **Rate Limited**: 120 طلب/دقيقة
- **Cached Results**: نتائج محفوظة لمدة دقيقتين
- **Fast Response**: استخدام `istartswith` للسرعة
- **Limited Results**: 5 نتائج من كل نوع

#### Request Example
```bash
GET /api/search/quick/?q=ah
```

#### Response Example
```json
{
    "query": "ah",
    "quick_results": [
        {
            "type": "user",
            "id": 1,
            "username": "ahmed123",
            "display_name": "Ahmed Mohamed",
            "avatar": "http://localhost:8000/media/avatars/1/avatar.jpg",
            "followers_count": 150
        },
        {
            "type": "tag",
            "name": "adventure",
            "display_name": "#adventure",
            "trips_count": 25
        }
    ],
    "total_results": 2,
    "has_more": true
}
```

---

### Search Suggestions API

#### Endpoint
```
GET /api/search/suggestions/?q={search_term}&limit={limit}
```

#### Description
اقتراحات البحث المبنية على الشعبية والكلمات الشائعة.

#### Parameters
| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| q | string | No | كلمة البحث (اختيارية للاقتراحات العامة) |
| limit | integer | No | عدد الاقتراحات (max: 20, default: 10) |

#### Request Example
```bash
GET /api/search/suggestions/?q=adv&limit=5
```

#### Response Example
```json
{
    "query": "adv",
    "suggestions": [
        {
            "text": "adventure",
            "display_text": "#adventure",
            "type": "tag",
            "popularity": 25
        },
        {
            "text": "ahmed_adventure",
            "display_text": "Ahmed Adventure",
            "type": "user",
            "popularity": 150
        }
    ]
}
```

---

### Search History API

#### Get Search History
```
GET /api/search/history/
```

**Authentication Required**

#### Response Example
```json
{
    "count": 15,
    "next": null,
    "previous": null,
    "results": [
        {
            "query": "adventure",
            "search_type": "unified",
            "results_count": 10,
            "created_at": "2024-08-19T15:30:00Z"
        },
        {
            "query": "ahmed",
            "search_type": "users",
            "results_count": 5,
            "created_at": "2024-08-19T15:25:00Z"
        }
    ]
}
```

#### Clear Search History
```
DELETE /api/search/history/clear/
```

**Authentication Required**

#### Response Example
```json
{
    "message": "تم مسح 15 عنصر من تاريخ البحث",
    "deleted_count": 15
}
```

---

### Popular Searches API

#### Endpoint
```
GET /api/search/popular/?limit={limit}
```

#### Description
الكلمات الأكثر بحثاً في النظام.

#### Request Example
```bash
GET /api/search/popular/?limit=10
```

#### Response Example
```json
{
    "popular_searches": [
        {
            "query": "adventure",
            "search_count": 1250,
            "last_searched": "2024-08-19T15:30:00Z"
        },
        {
            "query": "travel",
            "search_count": 980,
            "last_searched": "2024-08-19T15:28:00Z"
        }
    ],
    "total_count": 10
}
```

---

## ⚡ Performance & Caching

### Redis Caching
- **Quick Search**: 2 دقائق cache
- **Suggestions**: 5 دقائق cache
- **Popular Searches**: 10 دقائق cache

### Rate Limiting
- **Quick Search**: 120 طلب/دقيقة
- **Regular Search**: 60 طلب/دقيقة
- **Suggestions**: 100 طلب/دقيقة

### Database Optimization
- **Indexes** على جميع حقول البحث
- **istartswith** للبحث السريع
- **Limited results** للاستجابة السريعة

---

## 📱 Frontend Integration Examples

### JavaScript/React Example

#### Real-time Search Component
```javascript
import React, { useState, useEffect, useCallback } from 'react';
import { debounce } from 'lodash';

const RealTimeSearch = () => {
    const [query, setQuery] = useState('');
    const [results, setResults] = useState([]);
    const [suggestions, setSuggestions] = useState([]);
    const [loading, setLoading] = useState(false);
    const [history, setHistory] = useState([]);

    // Debounced search function
    const debouncedSearch = useCallback(
        debounce(async (searchQuery) => {
            if (searchQuery.length < 1) {
                setResults([]);
                return;
            }

            setLoading(true);
            try {
                const response = await fetch(
                    `/api/search/quick/?q=${encodeURIComponent(searchQuery)}`
                );
                const data = await response.json();

                if (response.ok) {
                    setResults(data.quick_results || []);
                } else {
                    console.error('Search error:', data.error);
                }
            } catch (error) {
                console.error('Network error:', error);
            } finally {
                setLoading(false);
            }
        }, 300), // 300ms debounce
        []
    );

    // Get suggestions
    const getSuggestions = async (searchQuery) => {
        try {
            const response = await fetch(
                `/api/search/suggestions/?q=${encodeURIComponent(searchQuery)}&limit=5`
            );
            const data = await response.json();

            if (response.ok) {
                setSuggestions(data.suggestions || []);
            }
        } catch (error) {
            console.error('Suggestions error:', error);
        }
    };

    // Load search history
    const loadHistory = async () => {
        try {
            const response = await fetch('/api/search/history/');
            const data = await response.json();

            if (response.ok) {
                setHistory(data.results?.slice(0, 5) || []);
            }
        } catch (error) {
            console.error('History error:', error);
        }
    };

    useEffect(() => {
        debouncedSearch(query);
        if (query.length > 0) {
            getSuggestions(query);
        } else {
            setSuggestions([]);
            loadHistory();
        }
    }, [query, debouncedSearch]);

    const handleResultClick = (result) => {
        if (result.type === 'user') {
            window.location.href = `/api/accounts/users/${result.id}/profile/`;
        } else if (result.type === 'tag') {
            window.location.href = `/api/trip/tags/${result.name}/trips/`;
        }
    };

    return (
        <div className="search-container">
            <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder="البحث عن مستخدمين أو تاجز..."
                className="search-input"
            />

            {loading && <div className="loading">جاري البحث...</div>}

            {/* Search Results */}
            {results.length > 0 && (
                <div className="search-results">
                    {results.map((result, index) => (
                        <div
                            key={index}
                            className="search-result-item"
                            onClick={() => handleResultClick(result)}
                        >
                            {result.type === 'user' ? (
                                <div className="user-result">
                                    {result.avatar && (
                                        <img src={result.avatar} alt="Avatar" />
                                    )}
                                    <div>
                                        <div className="display-name">{result.display_name}</div>
                                        <div className="username">@{result.username}</div>
                                        <div className="followers">{result.followers_count} متابع</div>
                                    </div>
                                </div>
                            ) : (
                                <div className="tag-result">
                                    <div className="tag-name">{result.display_name}</div>
                                    <div className="trips-count">{result.trips_count} رحلة</div>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}

            {/* Suggestions */}
            {suggestions.length > 0 && query.length > 0 && (
                <div className="suggestions">
                    <div className="suggestions-title">اقتراحات:</div>
                    {suggestions.map((suggestion, index) => (
                        <div
                            key={index}
                            className="suggestion-item"
                            onClick={() => setQuery(suggestion.text)}
                        >
                            {suggestion.display_text}
                        </div>
                    ))}
                </div>
            )}

            {/* Search History */}
            {history.length > 0 && query.length === 0 && (
                <div className="search-history">
                    <div className="history-title">البحثات الأخيرة:</div>
                    {history.map((item, index) => (
                        <div
                            key={index}
                            className="history-item"
                            onClick={() => setQuery(item.query)}
                        >
                            {item.query}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default RealTimeSearch;
```

#### Vanilla JavaScript Example
```javascript
class RealTimeSearch {
    constructor(inputElement, resultsElement) {
        this.input = inputElement;
        this.results = resultsElement;
        this.debounceTimer = null;

        this.init();
    }

    init() {
        this.input.addEventListener('input', (e) => {
            clearTimeout(this.debounceTimer);
            this.debounceTimer = setTimeout(() => {
                this.search(e.target.value);
            }, 300);
        });
    }

    async search(query) {
        if (query.length < 1) {
            this.results.innerHTML = '';
            return;
        }

        try {
            const response = await fetch(`/api/search/quick/?q=${encodeURIComponent(query)}`);
            const data = await response.json();

            if (response.ok) {
                this.displayResults(data.quick_results || []);
            } else {
                console.error('Search error:', data.error);
            }
        } catch (error) {
            console.error('Network error:', error);
        }
    }

    displayResults(results) {
        this.results.innerHTML = '';

        results.forEach(result => {
            const item = document.createElement('div');
            item.className = 'search-result-item';

            if (result.type === 'user') {
                item.innerHTML = `
                    <div class="user-result">
                        ${result.avatar ? `<img src="${result.avatar}" alt="Avatar">` : ''}
                        <div>
                            <div class="display-name">${result.display_name}</div>
                            <div class="username">@${result.username}</div>
                            <div class="followers">${result.followers_count} متابع</div>
                        </div>
                    </div>
                `;
                item.onclick = () => {
                    window.location.href = `/api/accounts/users/${result.id}/profile/`;
                };
            } else {
                item.innerHTML = `
                    <div class="tag-result">
                        <div class="tag-name">${result.display_name}</div>
                        <div class="trips-count">${result.trips_count} رحلة</div>
                    </div>
                `;
                item.onclick = () => {
                    window.location.href = `/api/trip/tags/${result.name}/trips/`;
                };
            }

            this.results.appendChild(item);
        });
    }
}

// Usage
const searchInput = document.getElementById('search-input');
const searchResults = document.getElementById('search-results');
const realTimeSearch = new RealTimeSearch(searchInput, searchResults);
```

### cURL Examples

#### Basic Search
```bash
# Search for users and tags
curl "http://localhost:8000/api/search/?q=ahmed"

# Search users only
curl "http://localhost:8000/api/search/users/?q=ahmed&page=1"

# Search tags only
curl "http://localhost:8000/api/search/tags/?q=adventure"

# Get user profile
curl "http://localhost:8000/api/accounts/users/1/profile/"

# Get trips by tag
curl "http://localhost:8000/api/trip/tags/adventure/trips/"
```

#### Real-time Search
```bash
# Quick search (type as you type)
curl "http://localhost:8000/api/search/quick/?q=ah"

# Get search suggestions
curl "http://localhost:8000/api/search/suggestions/?q=adv&limit=5"

# Get popular searches
curl "http://localhost:8000/api/search/popular/?limit=10"
```

#### Search History (Authentication Required)
```bash
# Get search history
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     "http://localhost:8000/api/search/history/"

# Clear search history
curl -X DELETE \
     -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     "http://localhost:8000/api/search/history/clear/"
```

#### Rate Limiting Test
```bash
# Test rate limiting (will return 429 after limit)
for i in {1..125}; do
    curl "http://localhost:8000/api/search/quick/?q=test$i"
    echo "Request $i completed"
done
```

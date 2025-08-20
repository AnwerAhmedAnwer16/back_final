# 🎨 دليل Frontend - مشروع Rahala

## 📋 جدول المحتويات
- [نظرة عامة](#نظرة-عامة)
- [إعداد المشروع](#إعداد-المشروع)
- [هيكل المشروع](#هيكل-المشروع)
- [Components الأساسية](#components-الأساسية)
- [State Management](#state-management)
- [API Integration](#api-integration)
- [UI/UX Guidelines](#uiux-guidelines)
- [Testing](#testing)

---

## 🎯 نظرة عامة

Frontend لمشروع Rahala مبني باستخدام **React.js** مع **TypeScript** لتوفير تجربة مستخدم متميزة وتفاعلية.

### التقنيات المستخدمة:
- ⚛️ **React 18** - مكتبة UI الأساسية
- 🔷 **TypeScript** - للـ type safety
- 🎨 **Tailwind CSS** - للتصميم
- 🔄 **Redux Toolkit** - لإدارة الحالة
- 📡 **Axios** - للـ HTTP requests
- 📱 **React Router** - للتنقل
- 🖼️ **React Hook Form** - لإدارة النماذج
- 📷 **React Dropzone** - لرفع الملفات

---

## ⚙️ إعداد المشروع

### 1. إنشاء مشروع React جديد:

```bash
# إنشاء المشروع
npx create-react-app rahala-frontend --template typescript
cd rahala-frontend

# تثبيت المكتبات المطلوبة
npm install @reduxjs/toolkit react-redux
npm install axios
npm install react-router-dom
npm install react-hook-form
npm install react-dropzone
npm install tailwindcss postcss autoprefixer
npm install @headlessui/react @heroicons/react
npm install react-hot-toast
npm install date-fns
npm install @types/node

# إعداد Tailwind CSS
npx tailwindcss init -p
```

### 2. إعداد Tailwind CSS:

```javascript
// tailwind.config.js
module.exports = {
  content: [
    "./src/**/*.{js,jsx,ts,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
        },
        secondary: {
          50: '#f0f9ff',
          500: '#06b6d4',
          600: '#0891b2',
        }
      },
      fontFamily: {
        'arabic': ['Cairo', 'sans-serif'],
      }
    },
  },
  plugins: [],
}
```

### 3. إعداد المتغيرات البيئية:

```env
# .env
REACT_APP_API_BASE_URL=http://localhost:8000/api
REACT_APP_MEDIA_BASE_URL=http://localhost:8000/media
REACT_APP_GOOGLE_CLIENT_ID=your-google-client-id
```

---

## 🏗️ هيكل المشروع

```
src/
├── components/          # مكونات قابلة للإعادة الاستخدام
│   ├── common/         # مكونات عامة
│   ├── forms/          # نماذج
│   ├── layout/         # تخطيط الصفحة
│   └── ui/            # مكونات UI أساسية
├── pages/              # صفحات التطبيق
│   ├── auth/          # صفحات المصادقة
│   ├── trips/         # صفحات الرحلات
│   └── profile/       # صفحات الملف الشخصي
├── hooks/              # Custom hooks
├── services/           # خدمات API
├── store/             # Redux store
├── types/             # TypeScript types
├── utils/             # دوال مساعدة
└── styles/            # ملفات CSS
```

---

## 🧩 Components الأساسية

### 1. TripCard Component:

```typescript
// components/trips/TripCard.tsx
import React from 'react';
import { Trip } from '../../types/trip';
import { formatDistanceToNow } from 'date-fns';
import { ar } from 'date-fns/locale';

interface TripCardProps {
  trip: Trip;
  onLike?: (tripId: number) => void;
  onComment?: (tripId: number) => void;
}

const TripCard: React.FC<TripCardProps> = ({ trip, onLike, onComment }) => {
  return (
    <div className="bg-white rounded-lg shadow-md overflow-hidden mb-6">
      {/* Header */}
      <div className="p-4 border-b">
        <div className="flex items-center justify-between">
          <div className="flex items-center space-x-3">
            <img
              src={trip.user.avatar || '/default-avatar.png'}
              alt={trip.user.username}
              className="w-10 h-10 rounded-full"
            />
            <div>
              <h3 className="font-semibold text-gray-900">{trip.user.username}</h3>
              <p className="text-sm text-gray-500">
                {formatDistanceToNow(new Date(trip.created_at), { 
                  addSuffix: true, 
                  locale: ar 
                })}
              </p>
            </div>
          </div>
          <div className="flex items-center space-x-2">
            <span className="text-sm text-gray-500">📍</span>
            <span className="text-sm font-medium">{trip.location}</span>
          </div>
        </div>
      </div>

      {/* Caption */}
      {trip.caption && (
        <div className="p-4">
          <p className="text-gray-800">{trip.caption}</p>
        </div>
      )}

      {/* Images */}
      {trip.images && trip.images.length > 0 && (
        <div className="grid grid-cols-2 gap-1">
          {trip.images.slice(0, 4).map((image, index) => (
            <img
              key={image.id}
              src={image.image}
              alt={`Trip image ${index + 1}`}
              className="w-full h-48 object-cover"
            />
          ))}
        </div>
      )}

      {/* Tourism Info */}
      {trip.tourism_info && (
        <TourismInfoCard 
          tourismInfo={trip.tourism_info}
          country={trip.country}
          city={trip.city}
        />
      )}

      {/* Actions */}
      <div className="p-4 border-t">
        <div className="flex items-center justify-between">
          <div className="flex space-x-4">
            <button
              onClick={() => onLike?.(trip.id)}
              className="flex items-center space-x-2 text-gray-600 hover:text-red-500"
            >
              <span>❤️</span>
              <span>{trip.likes_count || 0}</span>
            </button>
            <button
              onClick={() => onComment?.(trip.id)}
              className="flex items-center space-x-2 text-gray-600 hover:text-blue-500"
            >
              <span>💬</span>
              <span>{trip.comments_count || 0}</span>
            </button>
          </div>
          <button className="text-gray-600 hover:text-green-500">
            <span>📤</span>
          </button>
        </div>
      </div>
    </div>
  );
};

export default TripCard;
```

### 2. TourismInfoCard Component:

```typescript
// components/trips/TourismInfoCard.tsx
import React, { useState } from 'react';
import { TourismInfo } from '../../types/trip';

interface TourismInfoCardProps {
  tourismInfo: TourismInfo;
  country?: string;
  city?: string;
}

const TourismInfoCard: React.FC<TourismInfoCardProps> = ({ 
  tourismInfo, 
  country, 
  city 
}) => {
  const [isExpanded, setIsExpanded] = useState(false);

  if (!tourismInfo) return null;

  return (
    <div className="bg-gradient-to-r from-blue-500 to-purple-600 text-white m-4 rounded-lg overflow-hidden">
      {/* Header */}
      <div className="p-4 bg-black bg-opacity-20">
        <div className="flex items-center justify-between">
          <h3 className="text-lg font-bold">
            🌍 معلومات سياحية: {city}, {country}
          </h3>
          <button
            onClick={() => setIsExpanded(!isExpanded)}
            className="text-white hover:text-yellow-300"
          >
            {isExpanded ? '🔼' : '🔽'}
          </button>
        </div>
      </div>

      {/* Content */}
      <div className="p-4">
        {/* Description */}
        <div className="mb-4">
          <p className="text-sm leading-relaxed">
            {tourismInfo.description}
          </p>
        </div>

        {isExpanded && (
          <div className="space-y-4">
            {/* Recommended Places */}
            {tourismInfo.recommended_places && tourismInfo.recommended_places.length > 0 && (
              <div>
                <h4 className="font-semibold mb-2 flex items-center">
                  🏛️ أماكن مقترحة للزيارة
                </h4>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
                  {tourismInfo.recommended_places.map((place, index) => (
                    <div
                      key={index}
                      className="bg-white bg-opacity-20 rounded-lg p-2 text-sm"
                    >
                      📍 {place}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Warnings */}
            {tourismInfo.warnings && tourismInfo.warnings.length > 0 && (
              <div>
                <h4 className="font-semibold mb-2 flex items-center">
                  ⚠️ تحذيرات مهمة
                </h4>
                <div className="space-y-2">
                  {tourismInfo.warnings.map((warning, index) => (
                    <div
                      key={index}
                      className="bg-yellow-500 bg-opacity-30 border-l-4 border-yellow-300 rounded p-2 text-sm"
                    >
                      ⚠️ {warning}
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* Travel Info Grid */}
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              <div className="bg-white bg-opacity-20 rounded-lg p-3 text-center">
                <div className="text-2xl mb-1">💰</div>
                <div className="text-xs text-gray-200">العملة</div>
                <div className="text-sm font-semibold">{tourismInfo.currency}</div>
              </div>
              <div className="bg-white bg-opacity-20 rounded-lg p-3 text-center">
                <div className="text-2xl mb-1">🗣️</div>
                <div className="text-xs text-gray-200">اللغة</div>
                <div className="text-sm font-semibold">{tourismInfo.language}</div>
              </div>
              <div className="bg-white bg-opacity-20 rounded-lg p-3 text-center">
                <div className="text-2xl mb-1">📅</div>
                <div className="text-xs text-gray-200">أفضل وقت</div>
                <div className="text-sm font-semibold">{tourismInfo.best_time_to_visit}</div>
              </div>
              <div className="bg-white bg-opacity-20 rounded-lg p-3 text-center">
                <div className="text-2xl mb-1">🎯</div>
                <div className="text-xs text-gray-200">الأماكن</div>
                <div className="text-sm font-semibold">
                  {tourismInfo.recommended_places?.length || 0}
                </div>
              </div>
            </div>

            {/* Local Tips */}
            {tourismInfo.local_tips && tourismInfo.local_tips.length > 0 && (
              <div>
                <h4 className="font-semibold mb-2 flex items-center">
                  💡 نصائح محلية
                </h4>
                <div className="space-y-2">
                  {tourismInfo.local_tips.map((tip, index) => (
                    <div
                      key={index}
                      className="bg-green-500 bg-opacity-30 border-l-4 border-green-300 rounded p-2 text-sm"
                    >
                      💡 {tip}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default TourismInfoCard;
```

### 3. CreateTripForm Component:

```typescript
// components/forms/CreateTripForm.tsx
import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { useDropzone } from 'react-dropzone';
import { toast } from 'react-hot-toast';
import { tripService } from '../../services/tripService';

interface CreateTripFormData {
  caption: string;
  location: string;
  tags: string[];
}

const CreateTripForm: React.FC = () => {
  const [images, setImages] = useState<File[]>([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [tagInput, setTagInput] = useState('');

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    watch,
    setValue
  } = useForm<CreateTripFormData>({
    defaultValues: {
      tags: []
    }
  });

  const tags = watch('tags');

  // Dropzone للصور
  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'image/*': ['.jpeg', '.jpg', '.png', '.webp']
    },
    maxFiles: 5,
    maxSize: 5 * 1024 * 1024, // 5MB
    onDrop: (acceptedFiles) => {
      setImages(prev => [...prev, ...acceptedFiles].slice(0, 5));
    },
    onDropRejected: (rejectedFiles) => {
      rejectedFiles.forEach(file => {
        file.errors.forEach(error => {
          if (error.code === 'file-too-large') {
            toast.error('حجم الصورة كبير جداً (الحد الأقصى 5MB)');
          } else if (error.code === 'file-invalid-type') {
            toast.error('نوع الملف غير مدعوم');
          }
        });
      });
    }
  });

  const addTag = () => {
    if (tagInput.trim() && !tags.includes(tagInput.trim())) {
      setValue('tags', [...tags, tagInput.trim()]);
      setTagInput('');
    }
  };

  const removeTag = (tagToRemove: string) => {
    setValue('tags', tags.filter(tag => tag !== tagToRemove));
  };

  const removeImage = (indexToRemove: number) => {
    setImages(prev => prev.filter((_, index) => index !== indexToRemove));
  };

  const onSubmit = async (data: CreateTripFormData) => {
    if (images.length === 0) {
      toast.error('يجب إضافة صورة واحدة على الأقل');
      return;
    }

    setIsSubmitting(true);
    try {
      const formData = new FormData();
      formData.append('caption', data.caption);
      formData.append('location', data.location);
      
      // إضافة الصور
      images.forEach(image => {
        formData.append('images', image);
      });
      
      // إضافة التاجات
      data.tags.forEach(tag => {
        formData.append('tags', tag);
      });

      const result = await tripService.createTrip(formData);
      
      toast.success('تم إنشاء الرحلة بنجاح! 🎉');
      
      // إعادة تعيين النموذج
      reset();
      setImages([]);
      
      // عرض المعلومات السياحية إذا كانت متوفرة
      if (result.tourism_info) {
        toast.success('تم الحصول على معلومات سياحية ذكية! 🤖');
      }
      
    } catch (error: any) {
      toast.error(error.message || 'حدث خطأ أثناء إنشاء الرحلة');
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto bg-white rounded-lg shadow-md p-6">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">إنشاء رحلة جديدة</h2>
      
      <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
        {/* Caption */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            وصف الرحلة
          </label>
          <textarea
            {...register('caption', { required: 'وصف الرحلة مطلوب' })}
            rows={3}
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="اكتب وصفاً جميلاً لرحلتك..."
          />
          {errors.caption && (
            <p className="mt-1 text-sm text-red-600">{errors.caption.message}</p>
          )}
        </div>

        {/* Location */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            الموقع 📍
          </label>
          <input
            {...register('location', { required: 'الموقع مطلوب' })}
            type="text"
            className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
            placeholder="مثال: Cairo, Egypt"
          />
          {errors.location && (
            <p className="mt-1 text-sm text-red-600">{errors.location.message}</p>
          )}
          <p className="mt-1 text-xs text-gray-500">
            💡 سيتم الحصول على معلومات سياحية ذكية تلقائياً!
          </p>
        </div>

        {/* Tags */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            التاجات 🏷️
          </label>
          <div className="flex space-x-2 mb-2">
            <input
              type="text"
              value={tagInput}
              onChange={(e) => setTagInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && (e.preventDefault(), addTag())}
              className="flex-1 px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
              placeholder="أضف تاج..."
            />
            <button
              type="button"
              onClick={addTag}
              className="px-4 py-2 bg-blue-500 text-white rounded-md hover:bg-blue-600"
            >
              إضافة
            </button>
          </div>
          <div className="flex flex-wrap gap-2">
            {tags.map((tag, index) => (
              <span
                key={index}
                className="inline-flex items-center px-3 py-1 rounded-full text-sm bg-blue-100 text-blue-800"
              >
                {tag}
                <button
                  type="button"
                  onClick={() => removeTag(tag)}
                  className="ml-2 text-blue-600 hover:text-blue-800"
                >
                  ×
                </button>
              </span>
            ))}
          </div>
        </div>

        {/* Images Upload */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            الصور 📷 (مطلوب)
          </label>
          <div
            {...getRootProps()}
            className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
              isDragActive
                ? 'border-blue-500 bg-blue-50'
                : 'border-gray-300 hover:border-gray-400'
            }`}
          >
            <input {...getInputProps()} />
            <div className="text-gray-600">
              <div className="text-4xl mb-2">📷</div>
              {isDragActive ? (
                <p>اسحب الصور هنا...</p>
              ) : (
                <div>
                  <p>اسحب الصور هنا أو انقر للاختيار</p>
                  <p className="text-sm text-gray-500 mt-1">
                    الحد الأقصى: 5 صور، 5MB لكل صورة
                  </p>
                </div>
              )}
            </div>
          </div>

          {/* Preview Images */}
          {images.length > 0 && (
            <div className="mt-4 grid grid-cols-2 md:grid-cols-3 gap-4">
              {images.map((image, index) => (
                <div key={index} className="relative">
                  <img
                    src={URL.createObjectURL(image)}
                    alt={`Preview ${index + 1}`}
                    className="w-full h-32 object-cover rounded-lg"
                  />
                  <button
                    type="button"
                    onClick={() => removeImage(index)}
                    className="absolute top-2 right-2 bg-red-500 text-white rounded-full w-6 h-6 flex items-center justify-center text-sm hover:bg-red-600"
                  >
                    ×
                  </button>
                </div>
              ))}
            </div>
          )}
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isSubmitting}
          className={`w-full py-3 px-4 rounded-md text-white font-medium ${
            isSubmitting
              ? 'bg-gray-400 cursor-not-allowed'
              : 'bg-blue-500 hover:bg-blue-600'
          }`}
        >
          {isSubmitting ? (
            <div className="flex items-center justify-center">
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
              جاري الإنشاء...
            </div>
          ) : (
            '🚀 إنشاء الرحلة'
          )}
        </button>
      </form>
    </div>
  );
};

export default CreateTripForm;
```

---

## 🔄 State Management

### Redux Store Setup:

```typescript
// store/index.ts
import { configureStore } from '@reduxjs/toolkit';
import authSlice from './slices/authSlice';
import tripSlice from './slices/tripSlice';

export const store = configureStore({
  reducer: {
    auth: authSlice,
    trips: tripSlice,
  },
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
```

### Auth Slice:

```typescript
// store/slices/authSlice.ts
import { createSlice, createAsyncThunk, PayloadAction } from '@reduxjs/toolkit';
import { authService } from '../../services/authService';
import { User } from '../../types/user';

interface AuthState {
  user: User | null;
  token: string | null;
  isLoading: boolean;
  error: string | null;
}

const initialState: AuthState = {
  user: null,
  token: localStorage.getItem('token'),
  isLoading: false,
  error: null,
};

export const loginUser = createAsyncThunk(
  'auth/login',
  async (credentials: { email: string; password: string }) => {
    const response = await authService.login(credentials);
    localStorage.setItem('token', response.access);
    return response;
  }
);

export const registerUser = createAsyncThunk(
  'auth/register',
  async (userData: { email: string; username: string; password: string }) => {
    const response = await authService.register(userData);
    return response;
  }
);

const authSlice = createSlice({
  name: 'auth',
  initialState,
  reducers: {
    logout: (state) => {
      state.user = null;
      state.token = null;
      localStorage.removeItem('token');
    },
    clearError: (state) => {
      state.error = null;
    },
  },
  extraReducers: (builder) => {
    builder
      .addCase(loginUser.pending, (state) => {
        state.isLoading = true;
        state.error = null;
      })
      .addCase(loginUser.fulfilled, (state, action) => {
        state.isLoading = false;
        state.user = action.payload.user;
        state.token = action.payload.access;
      })
      .addCase(loginUser.rejected, (state, action) => {
        state.isLoading = false;
        state.error = action.error.message || 'Login failed';
      });
  },
});

export const { logout, clearError } = authSlice.actions;
export default authSlice.reducer;
```

---

## 📡 API Integration

### API Service:

```typescript
// services/api.ts
import axios from 'axios';
import { store } from '../store';
import { logout } from '../store/slices/authSlice';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://localhost:8000/api';

export const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor لإضافة التوكن
api.interceptors.request.use(
  (config) => {
    const token = store.getState().auth.token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor للتعامل مع الأخطاء
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      store.dispatch(logout());
    }
    return Promise.reject(error);
  }
);
```

### Trip Service:

```typescript
// services/tripService.ts
import { api } from './api';
import { Trip } from '../types/trip';

export const tripService = {
  async createTrip(formData: FormData): Promise<Trip> {
    const response = await api.post('/trip/create/', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  },

  async getTrips(page = 1): Promise<{ results: Trip[]; count: number }> {
    const response = await api.get(`/trip/?page=${page}`);
    return response.data;
  },

  async getTripById(id: number): Promise<Trip> {
    const response = await api.get(`/trip/${id}/`);
    return response.data;
  },

  async likeTrip(tripId: number): Promise<void> {
    await api.post('/interactions/like/', { trip_id: tripId });
  },

  async commentOnTrip(tripId: number, content: string): Promise<void> {
    await api.post('/interactions/comment/', { 
      trip_id: tripId, 
      content 
    });
  },
};
```

---

## 🎨 UI/UX Guidelines

### Design System:

```css
/* styles/globals.css */
@import 'tailwindcss/base';
@import 'tailwindcss/components';
@import 'tailwindcss/utilities';
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@300;400;600;700&display=swap');

/* Custom Components */
@layer components {
  .btn-primary {
    @apply bg-blue-500 hover:bg-blue-600 text-white font-medium py-2 px-4 rounded-lg transition-colors;
  }
  
  .btn-secondary {
    @apply bg-gray-200 hover:bg-gray-300 text-gray-800 font-medium py-2 px-4 rounded-lg transition-colors;
  }
  
  .card {
    @apply bg-white rounded-lg shadow-md p-6;
  }
  
  .input-field {
    @apply w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500;
  }
}

/* RTL Support */
[dir="rtl"] {
  font-family: 'Cairo', sans-serif;
}

/* Custom Animations */
@keyframes fadeIn {
  from { opacity: 0; transform: translateY(20px); }
  to { opacity: 1; transform: translateY(0); }
}

.fade-in {
  animation: fadeIn 0.5s ease-out;
}

/* Tourism Info Gradient */
.tourism-gradient {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* Loading Spinner */
.spinner {
  border: 2px solid #f3f3f3;
  border-top: 2px solid #3498db;
  border-radius: 50%;
  width: 20px;
  height: 20px;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}
```

### Responsive Design:

```typescript
// hooks/useResponsive.ts
import { useState, useEffect } from 'react';

export const useResponsive = () => {
  const [isMobile, setIsMobile] = useState(false);
  const [isTablet, setIsTablet] = useState(false);
  const [isDesktop, setIsDesktop] = useState(false);

  useEffect(() => {
    const checkDevice = () => {
      const width = window.innerWidth;
      setIsMobile(width < 768);
      setIsTablet(width >= 768 && width < 1024);
      setIsDesktop(width >= 1024);
    };

    checkDevice();
    window.addEventListener('resize', checkDevice);
    return () => window.removeEventListener('resize', checkDevice);
  }, []);

  return { isMobile, isTablet, isDesktop };
};
```

---

## 🧪 Testing

### Component Testing:

```typescript
// components/__tests__/TripCard.test.tsx
import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import TripCard from '../trips/TripCard';
import { Trip } from '../../types/trip';

const mockTrip: Trip = {
  id: 1,
  user: { username: 'testuser', avatar: null },
  caption: 'Test trip',
  location: 'Cairo, Egypt',
  country: 'مصر',
  city: 'القاهرة',
  tourism_info: {
    description: 'Test description',
    recommended_places: ['Place 1', 'Place 2'],
    warnings: ['Warning 1'],
    best_time_to_visit: 'Winter',
    local_tips: ['Tip 1'],
    currency: 'EGP',
    language: 'Arabic'
  },
  created_at: '2024-01-01T00:00:00Z',
  images: [],
  videos: [],
  tags: [],
  likes_count: 5,
  comments_count: 3
};

describe('TripCard', () => {
  it('renders trip information correctly', () => {
    render(<TripCard trip={mockTrip} />);
    
    expect(screen.getByText('testuser')).toBeInTheDocument();
    expect(screen.getByText('Test trip')).toBeInTheDocument();
    expect(screen.getByText('Cairo, Egypt')).toBeInTheDocument();
  });

  it('calls onLike when like button is clicked', () => {
    const mockOnLike = jest.fn();
    render(<TripCard trip={mockTrip} onLike={mockOnLike} />);
    
    const likeButton = screen.getByRole('button', { name: /❤️/ });
    fireEvent.click(likeButton);
    
    expect(mockOnLike).toHaveBeenCalledWith(1);
  });
});
```

### Integration Testing:

```typescript
// pages/__tests__/CreateTrip.test.tsx
import React from 'react';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { Provider } from 'react-redux';
import { store } from '../../store';
import CreateTripPage from '../CreateTripPage';

describe('CreateTripPage', () => {
  it('creates trip successfully', async () => {
    render(
      <Provider store={store}>
        <CreateTripPage />
      </Provider>
    );

    // Fill form
    fireEvent.change(screen.getByPlaceholderText('اكتب وصفاً جميلاً لرحلتك...'), {
      target: { value: 'Amazing trip to Cairo' }
    });
    
    fireEvent.change(screen.getByPlaceholderText('مثال: Cairo, Egypt'), {
      target: { value: 'Cairo, Egypt' }
    });

    // Submit form
    fireEvent.click(screen.getByText('🚀 إنشاء الرحلة'));

    await waitFor(() => {
      expect(screen.getByText('تم إنشاء الرحلة بنجاح! 🎉')).toBeInTheDocument();
    });
  });
});
```

---

**🎯 هذا الدليل يوفر كل ما تحتاجه لبناء frontend متميز لمشروع Rahala!**

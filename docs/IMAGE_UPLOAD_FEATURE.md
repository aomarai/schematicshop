# Image Upload Feature Implementation

## Overview
This implementation adds image upload and preview functionality for schematics, allowing users to showcase their builds with multiple images.

## Backend Changes

### New Model: SchematicImage
- **Location**: `backend/apps/schematics/models.py`
- **Fields**:
  - `id`: UUID primary key
  - `schematic`: Foreign key to Schematic
  - `image`: ImageField with validation for jpg, jpeg, png, webp
  - `caption`: Optional text description
  - `order`: Integer for sorting images
  - `created_at`: Timestamp

### API Endpoints
1. **Upload Image**: `POST /api/schematics/{id}/upload_image/`
   - Requires authentication and ownership
   - Max 10 images per schematic
   - Max 5MB per image
   - Validates file type (jpg, jpeg, png, webp)

2. **List Images**: `GET /api/schematics/{id}/images/`
   - Returns all images for a schematic
   - Publicly accessible if schematic is public

3. **Delete Image**: `DELETE /api/schematics/{id}/images/{image_id}/`
   - Requires authentication and ownership
   - Removes image from storage

### Database Migration
- **File**: `backend/apps/schematics/migrations/0004_add_schematic_images.py`
- Run with: `docker-compose exec backend python manage.py migrate`

## Frontend Changes

### New Components

#### ImageUpload Component
- **Location**: `frontend/src/components/ImageUpload.tsx`
- **Features**:
  - Drag-and-drop interface
  - Multiple image selection
  - Preview thumbnails with remove option
  - File size and type validation
  - Memory leak prevention with URL cleanup

#### ImageGallery Component
- **Location**: `frontend/src/components/ImageGallery.tsx`
- **Features**:
  - Grid layout for thumbnails
  - Lightbox view for full-size images
  - Navigation between images
  - Caption display
  - Keyboard navigation support

### Updated Pages

#### Upload Page (`frontend/src/pages/upload.tsx`)
- Added image upload section
- Sequential upload: schematic file first, then images
- Progress indicator showing current upload stage
- Supports up to 10 images per schematic

#### Schematic Detail Page (`frontend/src/pages/schematic/[id].tsx`)
- Displays first image as main thumbnail
- Shows image gallery below main content
- Lightbox functionality for viewing images
- Image count indicator

#### Schematic Grid (`frontend/src/components/SchematicGrid.tsx`)
- Uses first image as thumbnail if available
- Fallback to original thumbnail_url or placeholder

## Usage

### For Users
1. **Upload Schematic with Images**:
   - Go to Upload page
   - Select schematic file
   - Fill in details (title, description, etc.)
   - Add images by dragging/dropping or clicking to browse
   - Submit form

2. **View Schematic Images**:
   - Navigate to schematic detail page
   - View main image at top
   - Scroll to "Build Images" section
   - Click any image to open lightbox view
   - Use arrows or click to navigate

### For Developers

#### Running Migrations
```bash
docker-compose exec backend python manage.py migrate
```

#### Testing Image Upload
```bash
docker-compose exec backend pytest apps/schematics/tests.py::TestSchematicImages -v
```

#### Storage Configuration
Images are stored using the same storage backend as schematic files:
- **Development**: Local storage or MinIO
- **Production**: S3 or compatible object storage

Configure in `.env`:
```bash
USE_S3=1
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_STORAGE_BUCKET_NAME=your_bucket
AWS_S3_ENDPOINT_URL=https://your-s3-endpoint
```

## Security Considerations

### File Validation
- **Type**: Only jpg, jpeg, png, webp allowed
- **Size**: Max 5MB per image
- **Count**: Max 10 images per schematic

### Access Control
- Upload: Authenticated users only
- Delete: Owner only
- View: Based on schematic visibility (public/private)

### Storage
- Images stored securely in configured storage backend
- URLs generated with proper access controls
- Automatic cleanup on image deletion

## Performance Optimizations

### Backend
- Prefetch images with schematics in queries
- Index on (schematic, order) for fast retrieval
- Image URLs built with request context

### Frontend
- Lazy loading of images
- Preview thumbnails before upload
- URL cleanup to prevent memory leaks
- Progressive upload with status feedback

## Future Enhancements

Potential improvements for future iterations:
1. Image reordering (drag-and-drop)
2. Image editing (crop, resize)
3. Bulk image upload
4. Image compression/optimization
5. Thumbnail generation
6. Caption editing after upload
7. Multiple image deletion
8. Image moderation tools
9. AI-powered image tagging
10. 3D render preview generation

## Testing

### Unit Tests
All tests located in `backend/apps/schematics/tests.py`:
- `TestSchematicImages` class with 6 test methods
- Tests cover: upload, permissions, listing, deletion, limits

### Manual Testing Checklist
- [ ] Upload schematic with multiple images
- [ ] View images on detail page
- [ ] Open lightbox and navigate between images
- [ ] Delete images (owner only)
- [ ] Verify max limit enforcement
- [ ] Test with different image formats
- [ ] Check mobile responsiveness
- [ ] Verify image URLs work with S3/MinIO
- [ ] Test error handling for large files
- [ ] Check memory usage with multiple uploads

## Troubleshooting

### Images not displaying
1. Check storage configuration in `.env`
2. Verify bucket/directory permissions
3. Check CORS settings for S3/MinIO
4. Inspect browser console for errors

### Upload fails
1. Check file size (max 5MB)
2. Verify file type (jpg, jpeg, png, webp)
3. Ensure authenticated
4. Check available storage quota
5. Review server logs for errors

### Performance issues
1. Enable CDN for image delivery
2. Implement image compression
3. Use thumbnail generation
4. Enable browser caching
5. Optimize database queries

## Documentation Links
- [Django ImageField](https://docs.djangoproject.com/en/4.2/ref/models/fields/#imagefield)
- [DRF FileUploadParser](https://www.django-rest-framework.org/api-guide/parsers/#fileuploadparser)
- [React Dropzone](https://react-dropzone.js.org/)
- [Framer Motion](https://www.framer.com/motion/)

import io
import numpy as np
from fastapi import APIRouter, File, HTTPException, UploadFile
from PIL import Image
import torchvision.transforms as transforms
from torchvision.transforms import functional as F
import base64
from typing import List
import torch

router = APIRouter()

# Define standard transformations
standard_transforms = {
    'resize': transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
    ]),
    'color_jitter': transforms.Compose([
        transforms.ColorJitter(brightness=0.4, contrast=0.4, saturation=0.4, hue=0.1),
        transforms.ToTensor(),
    ]),
    'rotate': transforms.Compose([
        transforms.RandomRotation(30),
        transforms.ToTensor(),
    ]),
    'noise': transforms.Compose([
        transforms.ToTensor(),
        transforms.Lambda(lambda x: x + torch.randn_like(x).to(x.device) * 0.1),
    ]),
    'grayscale': transforms.Compose([
        transforms.Grayscale(3),  # 3 channels for compatibility
        transforms.ToTensor(),
    ]),
    'horizontal_flip': transforms.Compose([
        transforms.RandomHorizontalFlip(p=1.0),
        transforms.ToTensor(),
    ]),
    'vertical_flip': transforms.Compose([
        transforms.RandomVerticalFlip(p=1.0),
        transforms.ToTensor(),
    ]),
    'blur': transforms.Compose([
        transforms.GaussianBlur(kernel_size=(5, 5), sigma=(0.1, 2.0)),
        transforms.ToTensor(),
    ])
}

@router.post("/upload")
async def upload_image(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    content = await file.read()
    image = Image.open(io.BytesIO(content))
    
    # Convert to RGB if needed
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    # Convert to base64 for frontend display
    buffered = io.BytesIO()
    image.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    
    return {"content": f"data:image/png;base64,{img_str}"}

@router.post("/transform")
async def transform_image(file: UploadFile = File(...), transformation: str = None):
    try:
        if not file.content_type.startswith("image/"):
            raise HTTPException(status_code=400, detail="File must be an image")
        
        if transformation not in standard_transforms:
            raise HTTPException(status_code=400, detail="Invalid transformation type")
        
        content = await file.read()
        image = Image.open(io.BytesIO(content))
        
        if image.mode != 'RGB':
            image = image.convert('RGB')
        
        # Apply transformation
        transform = standard_transforms[transformation]
        transformed_image = transform(image)
        
        # Convert back to PIL Image
        if isinstance(transformed_image, torch.Tensor):
            transformed_image = F.to_pil_image(transformed_image.cpu())
        
        # Convert to base64
        buffered = io.BytesIO()
        transformed_image.save(buffered, format="PNG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        return {
            "transformed": f"data:image/png;base64,{img_str}",
            "type": transformation
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error processing image: {str(e)}")

@router.post("/batch_transform")
async def batch_transform(file: UploadFile = File(...), transformations: List[str]):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    content = await file.read()
    image = Image.open(io.BytesIO(content))
    
    if image.mode != 'RGB':
        image = image.convert('RGB')
    
    results = []
    for transform_type in transformations:
        if transform_type in standard_transforms:
            transform = standard_transforms[transform_type]
            transformed = transform(image)
            
            if isinstance(transformed, torch.Tensor):
                transformed = F.to_pil_image(transformed)
            
            buffered = io.BytesIO()
            transformed.save(buffered, format="PNG")
            img_str = base64.b64encode(buffered.getvalue()).decode()
            
            results.append({
                "type": transform_type,
                "image": f"data:image/png;base64,{img_str}"
            })
    
    return {"results": results}

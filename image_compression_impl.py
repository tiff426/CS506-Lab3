import numpy as np
from PIL import Image

# Function to load and preprocess the image
def load_image(image_path):
    image = Image.open(image_path) # add name
    data = np.asarray(image)
    return data

# Function to perform SVD on a single channel of the image matrix
def compress_channel_svd(channel_matrix, rank):
    U, S, Vt = np.linalg.svd(channel_matrix, full_matrices=False)   # don't want full matrices since we want compressed, only necessary data
    S_compressed = np.zeros((rank, rank))
    np.fill_diagonal(S_compressed, S[:rank])
    # u and Vt contain vectors that correspond to the singular values
    U_compressed = U[:, :rank]
    Vt_compressed = Vt[:rank, :]
    compressed_channel = np.dot(U_compressed, np.dot(S_compressed, Vt_compressed))
    return compressed_channel

# Function to perform SVD for image compression
def image_compression_svd(image_np, rank):
    # Check if the image is grayscale or color image
    if len(image_np.shape) == 2:  # Grayscale, so only 2 channels
        compressed_img = compress_channel_svd(image_np, rank)
    else:
        # List to store compressed channels
        compressed_channels = []
        
        # Loop over the 3 color channels (RGB)
        for i in range(3):
            channel = image_np[:, :, i]
            compressed_channel = compress_channel_svd(channel, rank)
            compressed_channels.append(compressed_channel)
        
        # Stack the compressed channels back into an RGB image
        compressed_img = np.stack(compressed_channels, axis=2)
        
    # Clip values to ensure they remain in the valid pixel range [0, 255]
    compressed_img = np.clip(compressed_img, 0, 255)
    
    return compressed_img.astype(np.uint8)

# Function to concatenate and save the original and quantized images side by side
def save_result(original_image_np, quantized_image_np, output_path):
    # Convert NumPy arrays back to PIL images
    original_image = Image.fromarray(original_image_np)
    quantized_image = Image.fromarray(quantized_image_np)
    
    # Get dimensions
    width, height = original_image.size
    
    # Create a new image that will hold both the original and quantized images side by side
    combined_image = Image.new('RGB', (width * 2, height))
    
    # Paste original and quantized images side by side
    combined_image.paste(original_image, (0, 0))
    combined_image.paste(quantized_image, (width, 0))
    
    # Save the combined image
    combined_image.save(output_path)
    
if __name__ == '__main__':
    # Load and process the image
    image_path = 'flower.png'  
    output_path = 'compressed_image.png'  
    image_np = load_image(image_path)

    # Perform image quantization using SVD
    rank = 2  # Rank for SVD, you may change this to experiment
    quantized_image_np = image_compression_svd(image_np, rank)

    # Save the original and quantized images side by side
    save_result(image_np, quantized_image_np, output_path)

import requests
import os
from datetime import datetime
import json
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BingImageDownloader:
    def __init__(self, save_dir="bing_images"):
        """
        Initialize the downloader with a save directory
        
        Args:
            save_dir (str): Directory to save downloaded images
        """
        self.save_dir = save_dir
        self.bing_api_url = "https://www.bing.com/HPImageArchive.aspx?format=js&idx=0&n=1"
        self.bing_base_url = "https://www.bing.com"
        
        # Create save directory if it doesn't exist
        if not os.path.exists(save_dir):
            os.makedirs(save_dir)
            logger.info(f"Created directory: {save_dir}")

    def get_image_url(self):
        """
        Fetch the URL of today's Bing image
        
        Returns:
            str: Full URL of the image
        """
        try:
            response = requests.get(self.bing_api_url)
            response.raise_for_status()
            data = response.json()
            
            # Extract image URL and metadata
            image_data = data["images"][0]
            image_url = self.bing_base_url + image_data["url"]
            
            return image_url, image_data
            
        except requests.RequestException as e:
            logger.error(f"Error fetching image URL: {str(e)}")
            raise

    def download_image(self):
        """
        Download the Bing image of the day
        
        Returns:
            str: Path to the downloaded image
        """
        try:
            # Get image URL and metadata
            image_url, image_data = self.get_image_url()
            
            # Generate filename with date and title
            date_str = datetime.now().strftime("%Y%m%d")
            title = image_data.get("title", "bing_image").replace(" ", "_")
            filename = f"{date_str}_{title}.jpg"
            file_path = os.path.join(self.save_dir, filename)
            
            # Check if file already exists
            if os.path.exists(file_path):
                logger.info(f"Image already exists: {file_path}")
                return file_path
            
            # Download image
            response = requests.get(image_url, stream=True)
            response.raise_for_status()
            
            # Save image
            with open(file_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            
            logger.info(f"Successfully downloaded image: {file_path}")
            
            # Save metadata
            metadata_file = os.path.join(self.save_dir, f"{date_str}_metadata.json")
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(image_data, f, indent=4)
            
            return file_path
            
        except Exception as e:
            logger.error(f"Error downloading image: {str(e)}")
            raise

def main():
    """
    Main function to run the downloader
    """
    try:
        downloader = BingImageDownloader()
        image_path = downloader.download_image()
        print(f"Image downloaded successfully to: {image_path}")
    except Exception as e:
        print(f"Error: {str(e)}")

if __name__ == "__main__":
    main()

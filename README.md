# Share Store

## Description  

Share Store allows users to register, log in, upload files, and manage access permissions for those files. Users can share their files with specific individuals or make them accessible to everyone. Additionally, users can view files shared with them by others. Share Store employs **Cloudinary** for file storage and retrieval. It provides features like user authentication, file upload/download, access control, password change, and account deletion, making it a versatile file-sharing platform.

[Project Demo](https://sharest.onrender.com)

## Updates
- **Discord Integration:** Enhanced the platform with a new feature that automates the process of uploading files `(college lecture slides in my case)` to Discord. Now, when users upload files containing specific keywords (e.g., lecture names or topics like Math or TOC) from their accounts, these files are automatically sent to a designated Discord channel, as specified in the environment variables. This integration eliminates the need for manual file transfers, saving time and ensuring that the content is promptly shared with the relevant Discord community.

**Screenshots**  

<section style="text-align:center" align="center">
    <img src='screenshots/login.png?raw=true' alt='Files posted/uploaded by a discord bot to a specific thread/channel.' width='250px' />
</section>
<section style="text-align:center" align="center">
    <img src='screenshots/register.png?raw=true' alt='Files posted/uploaded by a discord bot to a specific thread/channel.' width='250px' />
</section>
<section style="text-align:center" align="center">
    <img src='screenshots/app.png?raw=true' alt='Files posted/uploaded by a discord bot to a specific thread/channel.' width='250px' />
</section>
<section style="text-align:center" align="center">
    <img src='screenshots/app2.png?raw=true' alt='Files posted/uploaded by a discord bot to a specific thread/channel.' width='250px' />
</section>
<section style="text-align:center" align="center">
    <img src='screenshots/app3.png?raw=true' alt='Files posted/uploaded by a discord bot to a specific thread/channel.' width='250px' />
</section>
### Distinctiveness and Complexity
1. **Distinctiveness**:
    - **Unique Purpose**: Share Store specializes in secure file sharing and storage, setting it apart from traditional social networks or e-commerce sites.
    - **Targeted File Sharing**: Its main focus is on organized file sharing, not social interactions or product sales. The recent addition of Discord integration for file (automatic lecture slide) uploads further enhances its role as a specialized platform for content sharing.
    - **Cloudinary Integration**: Share Store integrates with Cloudinary, enhancing file management and enabling secure uploads and downloads.
2. **Complexity**:
    - **Django Backend**: Utilizes Django for user authentication, file metadata, and access control.
    - **JavaScript and Bootstrap**: Employs JavaScript and Bootstrap for a responsive frontend.
    - **User Authentication**: Implements secure user registration and login.
    - **File Management**: Handles complex tasks like file uploads, downloads, and access permissions.

### What’s contained in files
1. **`static/drive`**: Contains JavaScript for handling access permissions, the application's logo, and a stylesheet for styling.
2. **`templates/drive`**: Contains HTML templates responsible for rendering web pages.
3. **`cloudinary.py`**: Initializes the Cloudinary SDK and creates references for managing file uploads and retrieval.
4. **`models.py`**: Defines data models for the application, including `File`, `User`, and `Share`.
5. **`tests.py`**: Includes database tests for creating files, shares, and users.
6. **`urls.py`**: Defines URL patterns for the 'drive' app.
7. **`utils.py`**: Contains a utility function for iterating over files fetched from external URLs.
8. **`views.py`**: Houses view functions that handle HTTP requests and define how web pages are rendered.
9. **`discord_integration.py`**: Manages the automation of uploading files to a specified Discord channel based on certain criteria, utilizing the Discord API.
10. **`requirements.txt`**: Lists external Python packages and dependencies required for the project.

### How to run Share Store

1. **Create a Virtual Environment (Optional)**:
   ```bash
   python -m venv myenv
   myenv\Scripts\activate  # Windows
   source myenv/bin/activate  # macOS/Linux
2. **Install Requirements:**:
   ```bash
   pip install -r requirements.txt

3. **Create .env File:**:
    ```bash
    CLOUDINARY_CLOUD_NAME="Your Cloudinary cloud name"
    CLOUDINARY_API_KEY="Your Cloudinary API key"
    CLOUDINARY_API_SECRET="Your Cloudinary API secret"
    SECRET_KEY="Your Django secret key"
    CONNECTION_STRING="Your database connection string (production only)"
    SERVER_ID="Your Discord Server ID"
    BOT_TOKEN="Your Discord Bot Token"
    CHANNEL_MAPPINGS={"substring_1": "Channel_ID_1", "substring_2": "Channel_ID_2"}
    P_USERNAME="Specific platform username whose files will be checked for Discord posting."
4. **Database Migrations:**
    ```bash
    python manage.py makemigrations
    python manage.py migrate

5. Run the Server:
   ```bash
   python manage.py runserver


6. Access the Application:
   Open a web browser and navigate to http://localhost:8000 to access the Share Store application.



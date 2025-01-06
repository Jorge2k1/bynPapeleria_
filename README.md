# Papelería Blanco y Negro

Papelería Blanco y Negro is a web-based project designed to simplify and streamline the process of printing and document management for a local stationery store. The platform allows customers to upload documents, configure printing options, and place orders, either for in-store pickup or home delivery. This project is aimed at enhancing the efficiency of the store's operations and improving the user experience for customers.

## Features

### 1. **Document Management**
- Customers can create folders to organize their documents.
- Each folder supports uploading multiple PDF files.
- Users can view the number of pages in each uploaded document.

### 2. **Customizable Printing Options**
- Users can configure printing settings for each folder, including:
  - Number of copies.
  - Color options (Black & White or Color).
  - Single or double-sided printing.
  - Binding options based on the number of pages.
- Additional comments can be provided for specific instructions.

### 3. **Cart Management**
- Users can add configured folders to the cart.
- Dynamic price calculation based on:
  - Pages, copies, and configuration.
  - Delivery method (pickup or home delivery).
- Real-time price updates to display subtotal, delivery fee, and total.

### 4. **Order Processing**
- Orders are stored in a PostgreSQL database for tracking and management.
- An email is sent to the store with the order details and customer-uploaded files attached.

### 5. **Responsive Design**
- The platform is fully responsive and adapts to different screen sizes, including desktops and mobile devices.

### 6. **User-Friendly Interface**
- Intuitive UI with buttons and icons for ease of navigation.
- Hover effects and animations for a modern look.
- Simple deletion options for folders and documents.

## Technologies Used

### Backend
- **Flask**: A lightweight Python framework for backend logic.
- **SQLAlchemy**: ORM for database management.
- **PostgreSQL**: Used as the main database.
- **PyMuPDF**: For counting pages in uploaded PDF files.
- **smtplib**: For sending order confirmation emails with attachments.

### Frontend
- **HTML/CSS**: For page structure and styling.
- **Bootstrap**: For a responsive and mobile-friendly design.
- **JavaScript**: For dynamic client-side interactions.

### Hosting
- **Railway**: For database hosting.
- **InfinityFree** (optional): Lightweight hosting for the frontend.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/papeleria-blanco-y-negro.git
   cd papeleria-blanco-y-negro
   ```

2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables:
   - Add your email credentials in `EMAIL_ADDRESS` and `EMAIL_PASSWORD`.
   - Update the `SQLALCHEMY_DATABASE_URI` with your PostgreSQL credentials.

4. Run the application:
   ```bash
   flask run
   ```

5. Access the application at `http://127.0.0.1:5000/`.

## Usage

1. **Create a Folder**: Click the folder icon to create a new folder.
2. **Upload Documents**: Select files to upload to the folder.
3. **Configure Printing**: Set options like copies, color, and binding.
4. **Add to Cart**: Update the cart with your folders and see the total cost.
5. **Place Order**: Submit your order for processing.
6. **Receive Confirmation**: An email will be sent to the store with all details and uploaded files.

## Folder Deletion
- Folders can be deleted using the delete icon (“X”) in the top-right corner of each folder.
- Deleting a folder removes its files and configuration from the session.

## Future Improvements
- User authentication for tracking orders.
- Payment gateway integration (e.g., PayPal, Stripe).
- Support for additional file types (e.g., images, Word documents).
- Advanced analytics for store administrators.

## Contribution

1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature/your-feature
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add your feature"
   ```
4. Push to the branch:
   ```bash
   git push origin feature/your-feature
   ```
5. Open a pull request.


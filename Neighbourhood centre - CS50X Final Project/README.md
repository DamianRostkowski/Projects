# Neighbourhood Centre

#### [Video Demo](https://youtu.be/0aq4WhwBHkI)

#### Description

"Neighbourhood Centre" is a social platform website built to facilitate neighborly communication. This application, developed using Flask, JavaScript, SQL, and jQuery, empowers users not only to post and comment but also to volunteer and send money to others.

### Running the Site

To run this site, ensure you have installed `matplotlib` via:
```
pip install matplotlib
```


### Database Structure

The database comprises five tables:

- **Users**: Contains user data and the name of their picture file.
- **Money**: Holds information about the cash balance of each user.
- **Posts**: Contains details about every user-generated post.
- **Likes**: Tracks user likes and dislikes on posts, updating accordingly.
- **Comments**: Enables users to leave comments on posts.

### Key Features

- **Registration and Login**: Modeled after Week 9, the system includes a profile picture upload feature using `enctype="multipart/form-data"` in the form.
- **Post Interaction**: Posts can be liked without page refresh using AJAX. Commenting on a post triggers a form's appearance on the site with a hidden input for the post ID.
- **Post Types**: Various post types like Normal, Donate (for fundraising goals), and Help (for assisting the needy) are available.
- **Post Filtering and Sorting**: Posts can be filtered by type through checkboxes and sorted by likes or publication date.
- **Adding Posts**: Requires a title, description, and post type. 'Donate' posts need a specified fundraising goal.
- **Manage Money**: Provides a straightforward system for depositing or withdrawing funds without direct banking connections.
- **About Section**: Presents an overview of the website's functionality.
- **Profile Editing**: Users can modify their name, password, and photo. Changes can be reset or saved by clicking corresponding buttons.
- **Graphical Representation**: The profile section includes a graph displaying the user's donation-receive money ratio, generated using matplotlib.
- **Post Editing**: Users can edit post titles, descriptions, or delete posts.

### Development Approach

Throughout development, I heavily referenced documentation and occasionally sought clarification from a friend or YouTube tutorials for practical examples and explanations.

### Inspirational Films

- [Ajax Tutorial](https://www.youtube.com/watch?v=nF9riePnm80&ab_channel=RedEyedCoderClub)
- [Matplotlib Tutorial](https://www.youtube.com/watch?v=MPiz50TsyF0&ab_channel=CoreySchafer)

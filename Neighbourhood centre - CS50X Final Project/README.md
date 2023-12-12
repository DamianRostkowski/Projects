# neighbourhood centre
#### Video Demo: https://youtu.be/0aq4WhwBHkI
#### Description:
```Neighbourhood centre is social platform website that allows neighbours to comunicate eachother. This application made by flask, javascript, sql and jquery allow us not only posting and commenting but also voluntering and send money for others.``` .

### To run this site you need to install matplotlib by
`pip install matplotlib`


I used database with five tables: users with data and name of picture file; money which contains information about cash balance of each user; posts that contains information about every post that users sends; likes which is added everytime user send like or dislike to new post changed if user change like for dislike or opposite and deleted if user click like or dislike again; comments that user can left under every post


Register and login system is very similar to this in Week9, modified with adding profile picture which is sends to users folder in photos. To send it I used enctype="multipart/form-data" on the formulage. Main site displays posts which can be liked without refreshing site by using ajax and be commented by other users - after click comment the formulage is displayed in front of whole site with hidden input with id of post which is commenting. Posts have few types - Normal,  Donate which is used to send money for users' goals and help that allow one user to declare help for needy.

Posts can be filtered by left panel using checkboxed with types of post. It works on modification sql ask based on choosen options. We can also sort post by likes and publish data. I used ajax again, this time to implement in-real-time users searching.


Add post is not complicated: You must input title, description and choose type of it. If type is donate, you have to write your goal to collect.


To change your money balance you have to view Manage Money. In there you have simple system without connected any bank transactions system (yet :). After input ammount you can choose what to do with it - deposit to add founds or withdraw to remove it from your account (if you withdraw to much money you would get communicate).


About is a presentattion about functionality of website.


After click our name in top-right corner we can log-out or enter to edit profile. In second scenario we can see name, password and photo buttons. After click it website allow us to change every of this field. After click buttons again the changes are reset to previous one. To save changes you must click green button on top. Under this form is placed a graph with informations about our donate-recevie money ratio. To make graph i used matplotlib libary and save the graph in the webSite folder in photos. If edit profile is open every time, the old graph is deleted and new one is moving on it place. On this subpage there are your post edit part. You can click edit button for every of your posts. After it you can edit title and description or delete it.


To make this site I used documentation or if I still didn't know how to implement something I asked my friend for clarification or search films on youtube that explains and gift me example of it.

Films I got inspiration from:

[Film about ajax](https://www.youtube.com/watch?v=nF9riePnm80&ab_channel=RedEyedCoderClub).

[Film about matplotlib](https://www.youtube.com/watch?v=MPiz50TsyF0&ab_channel=CoreySchafer).

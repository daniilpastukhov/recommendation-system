# Game recommendation system
The goal of the project was making a web application with a content-based recommendation system. All recommendations are based on the Steam games dataset (you can find it in `data` folder). In order to be able to get recommendations, the user must rate at least few games, then the system will have enough information to propose new games.   
Recommendation system is based on the genres and categories of games user likes/dislikes. It allows to get more relevant and 
various list of games. Getting new recommendations is quite fast, it requires some linear oprations and matrix multiplications, which can be done relatively fast.   
In general, the total outcome of the project is sufficient, it gives reasonable recommendations, while there are few more options how to enhance the results.

The application is deloyed on `heroku.com`.   
You need to sign up or log in to use the application.

### Demo user
Login: test@test.com  
Password: 12345678

# Interface
- You can rate (like/dislike) games
- You can open your profile and change your preferences
- You can search for a concrete game
- You can get new recommendations

# How it looks like
![](assets/app.png)

# Technology
- Python (Flask, numpy, pandas)
- Nuxt.js
- MongoDB (cloud)

# Improvements 
There are at least few options how to improve relevance of the results:
- Use clustering algorithm to find similar games and use it to enhence the results
- Use more features

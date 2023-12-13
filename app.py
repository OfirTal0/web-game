from flask import Flask, render_template, request, redirect, session
import random
from db import query, insert_new_user,get_users,check_new_score
app = Flask(__name__)


app.secret_key = 'OfirTalCode'

def top_users():
    users = get_users()
    sorted_users = sorted(users, key=lambda x:x['score'], reverse=True)
    top_three = sorted_users[:3]
    return top_three

@app.route('/', methods = ['POST', 'GET'])
def home():
    top_users_profiles = top_users()
    username1= top_users_profiles[0]["username"]
    userscore1=top_users_profiles[0]["score"]
    userimg1=top_users_profiles[0]["profileimg"]
    username2= top_users_profiles[1]["username"]
    userscore2=top_users_profiles[1]["score"]
    userimg2=top_users_profiles[1]["profileimg"]
    username3= top_users_profiles[2]["username"]
    userscore3=top_users_profiles[2]["score"]
    userimg3=top_users_profiles[2]["profileimg"]
    if 'username' in session:
        username = session['username']
        profileimg = session['profileimg']
        permission = session['permission']
        return render_template('dashbord.html',permission=permission,action='Display',login=True, username=username, profileimg=profileimg,username1=username1,username2=username2, username3=username3,userscore1=userscore1,userscore2=userscore2,userscore3=userscore3,userimg1=userimg1,userimg2=userimg2,userimg3=userimg3)
    else:
        permission=''
        return render_template('dashbord.html',permission='', username='', profileimg='', login=False,username1=username1,username2=username2, username3=username3,userscore1=userscore1,userscore2=userscore2,userscore3=userscore3,userimg1=userimg1,userimg2=userimg2,userimg3=userimg3)

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "GET":
        if 'username' in session:
            return redirect('/')
        return render_template("login.html")
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        existing_users=query(f"SELECT * FROM users WHERE username = '{username}' AND password='{password}'")
        if existing_users:
            user_data = existing_users[0]
            session['username'] = user_data[1]
            session['profileimg'] = user_data[3]
            session['permission'] = user_data[6]
            return redirect('/')
        else:
            return render_template('login.html', error='No user was found, please sign up')

@app.route('/logout', methods=['POST', 'GET'])
def logout():
    session.pop('username', None)
    session.pop('profileimg', None)
    session.pop('admin',None)
    session.pop('permission',None)
    return redirect('/')

@app.route('/signup', methods = ['POST','GET'])
def signup(): 
        return render_template('signup.html')

@app.route('/register', methods = ['POST','GET'])
def register():
    username = request.form.get('username')
    existing_users=query(f"SELECT * FROM users WHERE username = '{username}'")
    if existing_users:
        return render_template('signup.html',error = f'username already exist. Please choose another')
    password = request.form.get('password')
    profileimg = request.form.get('profileimg')
    country = request.form.get('country')
    permission = 'view'
    insert_new_user(values=f"'{username}', '{password}', '{profileimg}', '{country}', 0, '{permission}'")  
    try:
        if session['permission']=='admin':
            selected_users = query(f"SELECT username, password, profileimg, country, score FROM 'users'")
            return render_template('admin.html',action='Display',users=selected_users,permission= session['permission'])
    except:
        session['username'] = username
        session['profileimg'] = profileimg
        session['permission'] = 'view'
        return redirect('/')


@app.route('/reset_my_password', methods = ['POST','GET'])
def reset_my_password():
    if request.method == "GET":
        return render_template("reset_password.html")
    else:
        username = request.form.get('username')
        new_password = request.form.get('new_password')
        verify_password = request.form.get('verify_password')
        if new_password == verify_password:
            user = query(sql = f"SELECT username FROM users WHERE username='{username}'")
            if len(user) > 0:
                query(sql = f"UPDATE users SET password = '{new_password}' WHERE username='{username}'")
                return render_template("login.html")
            else:
                error = 'no such user was found'
                return render_template("reset_password.html", error = error)
        else:
            error = 'The passwords do not match, try again'
            return render_template("reset_password.html", error = error)


#trivia game

def get_trivia_data_dict():
    existing_trivia_data=query(sql = f"SELECT * FROM trivia_data", db_name="games.db")
    trivia_data_dict = []
    keys = ["id","category","question","option_a","option_b","option_c","option_d","correct_answer","use"]
    for row in existing_trivia_data:
        row = list(row)
        my_dict= dict(zip(keys,row))
        trivia_data_dict.append(my_dict)
    return trivia_data_dict

@app.route('/trivia_game_start', methods = ['POST','GET'])
def trivia_game_start(): 
    global user_trivia
    user_trivia = {"points":0,"mistakes":0}
    query(sql = f"UPDATE trivia_data SET use = 'no'", db_name="games.db")
    if 'username' in session:
        username = session['username']
        profileimg = session['profileimg']
        return render_template('trivia_game.html',trivia_display = 'start', username=username, profileimg=profileimg, points=user_trivia["points"])
    else:
        return render_template('login.html')

def get_avalible_ques():
    avalible_ques = query(sql = f"SELECT * FROM trivia_data WHERE use = 'no'", db_name="games.db")
    avalible_ques_dict = []
    keys = ["id","category","question","option_a","option_b","option_c","option_d","correct_answer","use"]
    for row in avalible_ques:
        row = list(row)
        my_dict= dict(zip(keys,row))
        avalible_ques_dict.append(my_dict)
    return avalible_ques_dict
 
def get_avalible_categories_list():
    categories_list = []
    avalible_ques = get_avalible_ques()
    for ques in avalible_ques:
        categories_list.append(ques["category"])
    avalible_categories = set(categories_list)
    avalible_categories = list(avalible_categories)
    return avalible_categories


@app.route('/trivia_game_options', methods = ['POST', 'GET'])
def trivia_game_options():
    global user_trivia
    username = session['username']
    profileimg = session['profileimg']
    if user_trivia["mistakes"] == 3:
        message = f'You were wrong 3 times!  Game Over'
        return render_template('trivia_game.html',trivia_display = 'endgame', message = message, username=username, profileimg=profileimg, points=user_trivia["points"] )
    avalible_categories = get_avalible_categories_list()
    if len(avalible_categories) == 1: 
        category1 = avalible_categories[0]
        category2 = avalible_categories[0]
    elif len(avalible_categories) == 0:
        message = f'No more questions left. Your score is {user_trivia["points"]}, Great Job! '
        return render_template('trivia_game.html',trivia_display = 'endgame', message = message, username=username, profileimg=profileimg, points=user_trivia["points"])
    else:
        category1, category2 = random.sample(avalible_categories, 2)
    return render_template('trivia_game.html',trivia_display = 'options', username=username, profileimg=profileimg, points=user_trivia["points"], category1=category1, category2=category2)

@app.route('/trivia_questions', methods = ['POST', 'GET'])
def questiongame():
    global user_trivia
    global correct_answer
    username = session['username']
    profileimg = session['profileimg']
    choosen_category = request.form["category"]
    avalible_ques = query(sql = f"SELECT * FROM trivia_data WHERE use = 'no' and category == '{choosen_category}'", db_name="games.db")
    avalible_ques_dict = []
    keys = ["id","category","question","option_a","option_b","option_c","option_d","correct_answer","use"]
    for row in avalible_ques:
        row = list(row)
        my_dict= dict(zip(keys,row))
        avalible_ques_dict.append(my_dict)
    rand_ques = random.choice(avalible_ques_dict)
    question = rand_ques["question"]
    option1 = rand_ques["option_a"]
    option2 = rand_ques["option_b"]
    option3 = rand_ques["option_c"]
    option4 = rand_ques["option_d"]
    correct_answer = rand_ques["correct_answer"]
    id = rand_ques["id"]
    query(sql = f"UPDATE trivia_data SET use = 'yes' WHERE id = '{id}'", db_name="games.db")
    return render_template('trivia_game.html',trivia_display = 'questions', username=username, profileimg=profileimg, points=user_trivia["points"], question=question,option1=option1,option2=option2,option3=option3,option4=option4, correct_answer=correct_answer )


@app.route('/trivia_answer', methods = ['POST', 'GET'])
def answer():
    global user_trivia
    global correct_answer
    username = session['username']
    profileimg = session['profileimg']
    answer = request.form["answer"]
    message = ""
    if answer == correct_answer:
        user_trivia["points"] += 2
        message = f'Good job! You got 2 points'
    else:
        user_trivia["mistakes"]+=1
        message = f'Wrong choice! Try again next time'
    return render_template('trivia_game.html',trivia_display = 'answers', username=username, profileimg=profileimg, points=user_trivia["points"], message=message)


@app.route('/trivia_endgame', methods = ['POST', 'GET'])
def endgame():
    global user_trivia
    points = user_trivia["points"]
    username = session['username']
    profileimg = session['profileimg']
    message = check_new_score(game="trivia",username=username,profileimg=profileimg,points=points)
    query(sql = f"UPDATE trivia_data SET use = 'no'", db_name="games.db")
    user_trivia["points"] = 0
    user_trivia["mistakes"] = 0
    return render_template('trivia_game.html',message =message, trivia_display = 'start', username=username, profileimg=profileimg, points=user_trivia["points"])



# simon game

@app.route('/simongame', methods = ['POST','GET'])
def simon_game_start(): 
    if 'username' not in session:
        return render_template('login.html')
    else:
        username = session['username']
        profileimg = session['profileimg']
        return render_template('simongame.html', username=username, profileimg=profileimg)


#memory game

@app.route('/memorygame', methods=['POST', 'GET'])
def memory_game():
    if 'username' not in session:
        return render_template('login.html')
    else:
        username = session['username']
        profileimg = session['profileimg']
        return render_template('memorygame.html',username=username, profileimg=profileimg)
    

#admin page

@app.route('/admin', methods=['POST', 'GET'])
def admin():
    selected_users = query(f"SELECT username, password, permission, profileimg, country, score FROM 'users'")
    return render_template('admin.html',action='Display',users=selected_users,permission= session['permission'])
   
@app.route('/adminaction', methods=['POST', 'GET'])
def adminaction():
    action = request.form.get('action')
    select_user =  request.form.get('selected_user')
    if action == 'Delete':
        sql = f"DELETE FROM users WHERE username = '{select_user}'"
        query(sql)
    elif action == 'Edit':
        global user_to_edit
        user_to_edit =  query(f"SELECT * FROM 'users' WHERE username='{select_user}'")
        if len(user_to_edit) == 0:
            error = "please select a user"
            selected_users = query(f"SELECT username, password, profileimg, country, score FROM 'users'")
            return render_template('admin.html',error=error,action='Display',users=selected_users,permission= session['permission'])
        id_to_edit = user_to_edit[0][0]
        username_to_edit=user_to_edit[0][1]
        password_to_edit= user_to_edit[0][2]
        profileimg_to_edit= user_to_edit[0][3]
        country_to_edit = user_to_edit[0][4]
        user_to_edit = {"id_to_edit":id_to_edit,"username_to_edit":username_to_edit,"password_to_edit":password_to_edit,"profileimg_to_edit":profileimg_to_edit,"country_to_edit":country_to_edit}
        return render_template('admin.html',country_to_edit=country_to_edit,profileimg_to_edit=profileimg_to_edit,password_to_edit=password_to_edit,username_to_edit=username_to_edit,action=action,permission= session['permission'])
    elif action == 'Add':
        return redirect('/signup')
    elif action == 'Display':
        selected_users = query(f"SELECT username, password, permission, profileimg, country, score FROM 'users'")
        return render_template('admin.html',action='Display',users=selected_users,permission= session['permission'])
    selected_users = query(f"SELECT username, password, permission, profileimg, country, score FROM 'users'")
    return render_template('admin.html',action='Display',users=selected_users,permission= session['permission'])

@app.route('/adminedit', methods=['POST', 'GET'])
def adminedit():
    global user_to_edit
    save_cancel = request.form.get('save_cancel')
    if save_cancel == "Save":
        id_to_update = user_to_edit["id_to_edit"]
        username_to_update = request.form.get('username')
        profileimg_to_update = request.form.get('profileimg')
        password_to_update = request.form.get('password')
        country_to_update = request.form.get('country')
        permission_to_update = request.form.get('permission')
        query(f"UPDATE users set username='{username_to_update}',permission='{permission_to_update}', profileimg='{profileimg_to_update}',password='{password_to_update}', country='{country_to_update}' WHERE id='{id_to_update}'")
        selected_users = query(f"SELECT username, password, permission, profileimg, country, score FROM 'users'")
        return render_template('admin.html',action='Display',users=selected_users,permission= session['permission'])
    elif save_cancel == "Cancel":
        selected_users = query(f"SELECT username, password, permission, profileimg, country, score FROM 'users'")
        return render_template('admin.html',action='Display',users=selected_users,permission= session['permission'])


@app.route('/search_user', methods=['POST', 'GET'])
def search_user():        
    text = request.form.get('search_text')
    error = ''
    results= query(f"SELECT username, password, permission, profileimg, country, score FROM users WHERE username LIKE '%{text}%' OR password LIKE '%{text}%' OR permission LIKE '%{text}%' OR profileimg LIKE '%{text}%' OR country LIKE '%{text}%'")
    if len(results) == 0:
        error= 'No results were found'
    return render_template('admin.html',error=error,action='Display',users=results,permission= session['permission'])



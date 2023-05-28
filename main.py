from flask import *
import sqlite3, hashlib, os
from werkzeug.utils import secure_filename
from pprint import pprint 

app = Flask(__name__)
app.secret_key = 'secretkey'
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = set(['jpeg', 'jpg', 'png', 'gif'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def islogged():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        if 'email' not in session:
            logged = False
        else:
            logged = True
    return logged


def getUserStatut():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        if islogged():
            cur.execute("SELECT statut FROM users WHERE email = '" + session['email'] + "'")
            statut = cur.fetchone()
            return statut[0]

def isAdmin():
    if getUserStatut() == 'A':
        return True
    else:
        return False

def isVendeur():
    if getUserStatut() == 'V':
        return True
    else:
        return False
    
def isClient():
    if getUserStatut() == 'C':
        return True
    else:
        return False
    

def getUserData():
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        if islogged():
            cur.execute("SELECT userId, username FROM users WHERE email = '" + session['email'] + "'")
            userId, username = cur.fetchone()
            if getUserStatut() == 'A':
                noOfItems = 0
            else: 
                cur.execute(f"SELECT count(produitId) FROM panier WHERE userId = {userId}")
                noOfItems = cur.fetchone()[0]
            return (userId, username, noOfItems)
        else:
            return (None, 'guest', 0)



@app.route("/")
def root():
    userId, username, noOfItems = getUserData()
    with sqlite3.connect('database.db') as conn:
        if isAdmin():
            return redirect(url_for('admin'))
        else:
            cur = conn.cursor()
            cur.execute('SELECT produitId, nom, prix, description, image FROM produits LIMIT 4')
            itemData = cur.fetchall()
            itemData = parse(itemData)   
            return render_template('home.html', itemData=itemData, logged=islogged(), username=username, noOfItems=noOfItems)


@app.route("/admin")
def admin():
    with sqlite3.connect('database.db') as conn:
        if isAdmin():
            cur = conn.cursor()
            cur.execute('SELECT userId, prenom, email, username FROM users')
            userData = cur.fetchall()
            cur.execute('SELECT produitId, nom, prix FROM produits')
            produitData = cur.fetchall()

            pprint(userData)
            pprint(produitData)
            return render_template('admin.html', logged=True, userData=userData, produitData=produitData)
        
        else:
            # erreur 
            return render_template('admin.html', logged=True)

@app.route("/toutParcourir")
def toutParcourir():
    userId, username, noOfItems = getUserData()
    with sqlite3.connect('database.db') as conn:
        if isAdmin():
            return render_template('admin.html', logged=True)
        else:
            cur = conn.cursor()
            cur.execute('SELECT produitId, nom, prix, description, image FROM produits')
            itemData = cur.fetchall()
            itemData = parse(itemData)   
            return render_template('toutParcourir.html', itemData=itemData, logged=islogged(), username=username, noOfItems=noOfItems)
            

@app.route("/supprimerUser", methods=["GET","POST"])
def supprimerUser():
    if request.method == "POST":
        userID = request.form['userId']
        with sqlite3.connect('database.db') as conn:
            try:
                cur = conn.cursor()
                cur.execute(f'DELETE FROM users WHERE userId = {userID};')
                
                conn.commit()
            except:
                conn.rollback()
                msg = "erreur"
        conn.close()  
        return redirect(url_for('admin'))


@app.route("/supprimerProduit2", methods=["GET","POST"])
def supprimerProduit2():
    if request.method == "POST":
        produitId = request.form['produitId']
        with sqlite3.connect('database.db') as conn:
            try:
                cur = conn.cursor()
                cur.execute(f'DELETE FROM produits WHERE produitId = {produitId};')
                
                conn.commit()
            except:
                conn.rollback()
                msg = "erreur"
        conn.close()  
        return redirect(url_for('admin'))


@app.route("/creerUser", methods = ['GET', 'POST'])
def creerUser():
    if request.method == 'POST':
        password = request.form['password']
        email = request.form['email']
        prenom = request.form['prenom']
        nom = request.form['nom']
        username = request.form['username']
        with sqlite3.connect('database.db') as con:
            try:
                cur = con.cursor()
                cur.execute('INSERT INTO users (password, email, username, nom, prenom, statut) VALUES (?, ?, ?, ?, ?, ?)', (hashlib.md5(password.encode()).hexdigest(), email, username, nom, prenom, 'V'))
                con.commit()
                msg = "Compte vendeur créé avec succès"
            except:
                con.rollback()
                msg = "erreur"
        con.close()
        return render_template("admin.html", erreur=msg, logged=True)


@app.route("/ajout")
def ajout():
    if not islogged():
        return render_template('login.html', erreur='')
    else:
        logged=True
        return render_template('ajout.html', logged=logged)


@app.route("/ajoutProduit", methods=["GET", "POST"])
def ajoutProduit():
    userId, username, noOfItems = getUserData()
    nom = request.form['nom']
    if not islogged():
        return render_template('login.html', erreur='')
    else:
        if request.method == "POST":
            if isAdmin() or isVendeur():   
                nom = request.form['nom']
                prix = float(request.form['prix'])
                description = request.form['description']

                image = request.files['image']
                if image and allowed_file(image.filename):
                    filename = secure_filename(image.filename)
                    image.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                nomImage = filename

                with sqlite3.connect('database.db') as conn:
                    try:
                        cur = conn.cursor()
                        cur.execute('''INSERT INTO produits (nom, prix, description, image, userId) VALUES ( ?, ?, ?, ?, ?)''', (nom, prix, description, nomImage, userId))                     
                        conn.commit()
                        msg="Ajout d'un produit réussie"
                    except:
                        msg="erreur"
                        conn.rollback()
                conn.close()    
            else:
                print('Il vous faut un compte vendeur pour pouvoir ajouter un article')
        return redirect(url_for('root'))


@app.route("/supprimer")
def remove():
    if islogged():
        if isClient():
            return render_template('home.html', erreur='', logged=True)
        else:
            with sqlite3.connect('database.db') as conn:
                cur = conn.cursor()
                cur.execute('SELECT produitId, nom, prix, description, image FROM produits')
                itemData = cur.fetchall()
                itemData = parse(itemData)  

            conn.close()
            return render_template('supprimer.html', itemData=itemData, logged=True)
    else:
        return redirect(url_for('root'))
    

@app.route("/supprimerProduit")
def removeItem():
    if isClient():
        pass
    else:
        produitId = request.args.get('produitId')
        with sqlite3.connect('database.db') as conn:
            try:
                cur = conn.cursor()
                if isAdmin():
                    cur.execute('DELETE FROM produits WHERE produitID = ' + produitId)
                else:
                    cur.execute('SELECT userId FROM produits where produitId = '+ produitId)
                    idToCheck = cur.fetchone()[0]
         
                    print(idToCheck)
                    print(getUserData()[0])

                    if idToCheck == getUserData()[0]:
                        print("toto")
                        cur.execute('DELETE FROM produits WHERE produitId = ' + produitId)
                        print("toto")
                        msg = "Suppression du produit réussie"

                    else:
                        msg = "Vous ne pouvez pas supprimer un produit d'un autre vendeur !"
                
                conn.commit()
            except:
                conn.rollback()
                msg = "erreur"
        conn.close()
        print(msg)

    return redirect(url_for('root'))

@app.route("/chercherUser", methods=["GET", "POST"])
def chercherUser():
    if request.method == "POST":
        if isAdmin():
            nom = request.form['search']
            try:

                with sqlite3.connect('database.db') as conn:
                    cur = conn.cursor()
                    cur.execute(f"SELECT nom, prenom, userId, email FROM users WHERE nom = {nom} ;")
                    userData = cur.fetchall()
            except:
                userData = None
            return render_template("admin.html", userData = userData)

@app.route("/loginForm")
def loginForm():
    if 'email' in session:
        return redirect(url_for('root'))
    else:
        return render_template('login.html', erreur='')

@app.route("/login", methods = ['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        if is_valid(email, password):
            session['email'] = email
            return redirect(url_for('root'))
        else:
            erreur = 'Invalid UserId / Password'
            return render_template('login.html', erreur=erreur)

@app.route("/detailProduit")
def detailProduit():
    userId, username, noOfItems = getUserData()
    produitId = request.args.get('produitId')
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT produitId, nom, prix, description, image FROM produits WHERE produitId = ' + produitId)
        produitData = cur.fetchone()
    conn.close()
    return render_template("detailProduit.html", data=produitData, logged=islogged(), username=username, noOfItems = noOfItems)

@app.route("/ajoutPanier")
def addTopanier():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    else:
        produitId = int(request.args.get('produitId'))
        with sqlite3.connect('database.db') as conn:
            cur = conn.cursor()
            cur.execute("SELECT userId FROM users WHERE email = '" + session['email'] + "'")
            userId = cur.fetchone()[0]
            try:
                cur.execute("INSERT INTO panier (userId, produitId) VALUES (?, ?)", (userId, produitId))
                conn.commit()
                msg = "Produit ajouté au panier !"
            except:
                conn.rollback()
                msg = "erreur"
        conn.close()
        return redirect(url_for('root'))

@app.route("/panier")
def panier():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    userId, username, noOfItems = getUserData()
    email = session['email']
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT userId FROM users WHERE email = '" + email + "'")
        userId = cur.fetchone()[0]
        cur.execute("SELECT produits.produitId, produits.nom, produits.prix, produits.image FROM produits, panier WHERE produits.produitId = panier.produitId AND panier.userId = " + str(userId))
        produits = cur.fetchall()
    totalprix = 0
    for row in produits:
        totalprix += row[2]
    return render_template("panier.html", produits = produits, totalprix=totalprix, logged=islogged(), username=username, noOfItems=noOfItems)

@app.route("/paiement", methods = ['GET', 'POST'])
def paiement():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    else:
        return render_template("paiement.html")


@app.route("/paiementForm", methods = ['GET', 'POST'])
def paiementForm():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    else:
        logged = True
        email = session['email']

        try:
            card_number = request.form['card_number']
            card_name = request.form['card_name']
            expiry_date = request.form['expiry_date']
            cvv = request.form['cvv']
            
            msg = "Paiement effectué avec succès !"
            with sqlite3.connect('database.db') as conn:
                cur = conn.cursor()
                cur.execute("SELECT userId FROM users WHERE email = '" + email + "'")
                userId = cur.fetchone()[0]
                try:
                    cur.execute("DELETE FROM panier WHERE userId = " + str(userId))
                    print(50*"#")
                except:
                    conn.rollback()
            conn.close()
            return render_template("home.html", logged=logged, erreur=msg)
        except:
            msg = "Votre carte n'est pas valide"
            return render_template("paiement.html", logged=logged, erreur=msg)

@app.route("/suppProduitPanier")
def suppProduitPanier():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    email = session['email']
    produitId = int(request.args.get('produitId'))
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT userId FROM users WHERE email = '" + email + "'")
        userId = cur.fetchone()[0]
        try:
            cur.execute("DELETE FROM panier WHERE userId = " + str(userId) + " AND produitId = " + str(produitId))
            conn.commit()
            msg = "Produit supprimé du panier"
        except:
            conn.rollback()
            msg = "erreur"
    conn.close()
    return redirect(url_for('root'))

@app.route("/logout")
def logout():
    session.pop('email', None)
    return redirect(url_for('root'))

def is_valid(email, password):
    con = sqlite3.connect('database.db')
    cur = con.cursor()
    cur.execute('SELECT email, password FROM users')
    data = cur.fetchall()
    for row in data:
        if row[0] == email and row[1] == hashlib.md5(password.encode()).hexdigest():
            return True
    return False


@app.route("/checkout", methods=['GET','POST'])
def payment():
    if 'email' not in session:
        return redirect(url_for('loginForm'))
    userId, username, noOfItems = getUserData()
    email = session['email']

    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute("SELECT produits.produitId, produits.nom, produits.prix, produits.image FROM produits, panier WHERE produits.produitId = panier.produitId AND panier.userId = " + str(userId))
        produits = cur.fetchall()
    totalprix = 0
    for row in produits:
        totalprix += row[2]
        print(row)
    #    cur.execute("INSERT INTO Orders (userId, produitId) VALUES (?, ?)", (userId, row[0]))
    cur.execute("DELETE FROM panier WHERE userId = " + str(userId))
    conn.commit()

        

    return render_template("checkout.html", produits = produits, totalprix=totalprix, logged=islogged(), username=username, noOfItems=noOfItems)

@app.route("/register", methods = ['GET', 'POST'])
def register():
    if request.method == 'POST':
        #Parse form data    
        password = request.form['password']
        email = request.form['email']
        prenom = request.form['prenom']
        nom = request.form['nom']
        username = request.form['username']

        with sqlite3.connect('database.db') as con:
            try:
                cur = con.cursor()
                cur.execute('INSERT INTO users (password, email, username, prenom, nom, statut) VALUES (?, ?, ?, ?, ?, ?)', (hashlib.md5(password.encode()).hexdigest(), email, username, prenom, nom, 'C'))
                con.commit()

                msg = "Inscription réussie"
            except:
                con.rollback()
                msg = "erreur"
        con.close()
        return render_template("login.html", erreur=msg)

@app.route("/registerationForm")
def registrationForm():
    return render_template("register.html")

def allowed_file(filename):
    return '.' in filename and \
            filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS

def parse(data):
    ans = []
    i = 0
    while i < len(data):
        curr = []
        for j in range(7):
            if i >= len(data):
                break
            curr.append(data[i])
            i += 1
        ans.append(curr)
    return ans

if __name__ == '__main__':
    app.run(debug=True)

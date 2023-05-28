import sqlite3, hashlib

conn = sqlite3.connect('database.db')


conn.execute('''CREATE TABLE IF NOT EXISTS users 
		(userId INTEGER PRIMARY KEY, 
		password TEXT,
		email TEXT,
		username TEXT,
		nom TEXT,
		prenom TEXT,
		statut TEXT
		)''')

conn.execute('''CREATE TABLE IF NOT EXISTS produits
		(produitId INTEGER PRIMARY KEY,
		nom TEXT,
		prix REAL,
		description TEXT,
		image TEXT,
		userId INTEGER,
		FOREIGN KEY(userId) REFERENCES users(userId)
		)''')

conn.execute('''CREATE TABLE IF NOT EXISTS panier
		(userId INTEGER,
		produitId INTEGER,
		FOREIGN KEY(userId) REFERENCES users(userId),
		FOREIGN KEY(produitId) REFERENCES produits(produitId)
		)''')


adminpass = 'admin'
cur = conn.cursor()

cur.execute('''
INSERT INTO users 
(password, email, username, prenom, nom, statut)
VALUES (?, ?, ?, ?, ?, ?)''', 
(hashlib.md5(adminpass.encode()).hexdigest(), 'admin@istrator.com', 'admin', '', '', 'A'))

vendeurpass = 'vendeur'
cur.execute('''
INSERT INTO users 
(password, email, username, prenom, nom, statut)
VALUES (?, ?, ?, ?, ?, ?)''', 
(hashlib.md5(vendeurpass.encode()).hexdigest(), 'vendeur@vendeur.com', 'vendeur', '', '', 'V'))

clientpass = 'client'
cur.execute('''
INSERT INTO users 
(password, email, username, prenom, nom, statut)
VALUES (?, ?, ?, ?, ?, ?)''', 
(hashlib.md5(clientpass.encode()).hexdigest(), 'client@client.com', 'client', '', '', 'C'))


cur.execute('''INSERT INTO produits 
(produitId ,nom , prix , description , image ,userId) 
VALUES (?,?,?,?,?,?)''', (1, 'Raspberry', 200, 'Raspberry Pi 4B, 2 GB RAM, WiFi & BT', '1.jpg', 1))

cur.execute('''INSERT INTO produits 
(produitId ,nom , prix , description , image ,userId) 
VALUES (?,?,?,?,?,?)''', (2, 'Flipper 0', 270, 'Flipper Zero is a portable multi-tool for pentesters and geeks in a toy-like body', '2.jpg', 1))

cur.execute('''INSERT INTO produits 
(produitId ,nom , prix , description , image ,userId) 
VALUES (?,?,?,?,?,?)''', (3, 'Ecouteurs sans fils', 250, 'Écouteurs sans fil avec réduction de bruit', '3.jpg', 1))

cur.execute('''INSERT INTO produits 
(produitId ,nom , prix , description , image ,userId) 
VALUES (?,?,?,?,?,?)''', (4, 'Enceinte Bluetooth', 70, 'Étanche, portable, puissante, sans fil.', '4.jpg', 1))

cur.execute('''INSERT INTO produits 
(produitId ,nom , prix , description , image ,userId) 
VALUES (?,?,?,?,?,?)''', (5, 'Routeur Wi-Fi 6 haute vitesse', 200, 'Connexion rapide, large couverture réseau.', '5.jpg', 1))

cur.execute('''INSERT INTO produits 
(produitId ,nom , prix , description , image ,userId) 
VALUES (?,?,?,?,?,?)''', (6, 'Nettoyeur à ultrasons', 44, "Le nettoyeur à ultrasons fait vibrer l'eau 48 000 fois par seconde pour éliminer la saleté cachée. Avec la fréquence de vibration domestique la plus élevée, la saleté protéinée peut être nettoyée, et cette saleté est attachée aux petites pièces et aux crevasses difficiles à traiter avec de l'eau. En générant des micro-vibrations dans l'eau, l'onde de vibration sonore pénètre dans le métal précieux que la brosse ne peut atteindre et nettoie les saletés tenaces.", '6.jpg', 1))

cur.execute('''INSERT INTO produits 
(produitId ,nom , prix , description , image ,userId) 
VALUES (?,?,?,?,?,?)''', (7, 'Casque de réalité virtuelle', 400, 'Expérience immersive, suivi des mouvements.', '7.jpg', 1))


cur.execute('''INSERT INTO produits 
(produitId ,nom , prix , description , image ,userId) 
VALUES (?,?,?,?,?,?)''', (8, 'Imprimante 3D de bureau', 1000, 'Impression précise, compatible avec divers matériaux.', '8.jpg', 1))

cur.execute('''INSERT INTO produits 
(produitId ,nom , prix , description , image ,userId) 
VALUES (?,?,?,?,?,?)''', (9, 'Drone avec caméra 4K', 1200, 'Caméra 4K stabilisée sur une nacelle à cardan, vol stable, modes de vol intelligents, transmission vidéo en direct.', '9.jpg', 1))


cur.execute('''INSERT INTO produits 
(produitId ,nom , prix , description , image ,userId) 
VALUES (?,?,?,?,?,?)''', (10, 'Smartwatch avec suivi de la santé', 400, 'Écran tactile, moniteur de fréquence cardiaque.', '10.jpg', 1))

conn.commit()
conn.close()


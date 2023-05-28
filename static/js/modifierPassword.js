function validate() {
    var pass = document.getElementById("password").value;
    var pass2 = document.getElementById("password2").value;
    if (pass == pass2) {
        return true;
    } else {
        alert("Les mots de passe ne correspondent pas");
        return false;
    }
}


"""
Routes and views for the flask application.
"""

from datetime import date, datetime
from flask import Flask, render_template, redirect, request, url_for, session, flash
from sqlalchemy import create_engine
import speech_recognition as SRG
from forms import studentlogin, register, Forgotpass
from werkzeug.security import generate_password_hash, check_password_hash

application = Flask(__name__)

# engine = create_engine('mysql+pymysql://root:Hack@1234@localhost:3306/lib') # connecting mysql database to flask using the create engine
engine = create_engine('mysql+pymysql://ulbvteneqf0x0bth:ohfbpR1KQar48ZCha6S8@bmojjbr7nkavrfmdqv1t-mysql.services.clever-cloud.com:3306/bmojjbr7nkavrfmdqv1t')
# connecting mysql database(clever cloud) to flask using the create engine
conn = engine.raw_connection()  # creating connection object to commit the action
cur = conn.cursor()  # creating cursor object to fetch and insert data from/into database

application.secret_key = "lib_software"  # for working of sessionscd library
application.config["SECRET_KEY"] = "fyndproject"  # for working of wtforms for form validation


@application.route('/')
@application.route('/home')  # home page
def home():
    """Renders the home page."""
    return render_template('home.html')


@application.route('/login/profile/feedback', methods=['GET', 'POST'])  # feedback page
def feedback():
    if request.method == "POST":
        na = request.form.get("name")
        us = request.form.get("email")
        yn = request.form.get('YorN')
        num = request.form.get('number')
        rate = request.form.get('rate')
        msg = request.form.get('textmsg')
        cur.execute("insert into review values(%s,%s,%s,%s,%s,%s)", (na, us, num, yn, rate, msg))
        conn.commit()
        return redirect(url_for('profile'))
    return render_template('feedback.html')


@application.route('/login', methods=['GET', 'POST'])  # login page
def login():
    form = studentlogin()
    if request.method == 'POST' and form.validate_on_submit():
        user = form.user.data
        pwd = form.pwd.data
        cur.execute("select username,password from student where username=%s", user)
        r = cur.fetchall()
        r = dict(r)
        #print(r)
        cur.execute("select username,role from roles where username=%s", user)  # using key:value pair
        r1 = cur.fetchall()
        r1 = dict(r1)
        if r:
            if check_password_hash(r[user], pwd) and r1[user] == "admin":
                session["user"] = user
                cur.execute("select fname,id from student where username=%s", user)
                i = cur.fetchone()
                fname = i[0]
                session["fname"] = fname
                session["role"] = r1[user]
                return redirect(url_for("admin"))  # directing to admin page if role is admin
            elif check_password_hash(r[user], pwd) and r1[user] == "student":
                session["user"] = user
                cur.execute("select fname,id from student where username=%s", user)
                i = cur.fetchone()
                fname = i[0]
                roll = i[1]
                session["fname"] = fname
                session["roll"] = roll
                session["role"] = r1[user]
                return redirect(url_for("profile"))  # directing to profile page if role is student
            else:
                flash("Invalid Password", "error")  # incorrect password
                return redirect(url_for('login'))
        else:
            flash("Incorrect Username", "error")  # incorrect username
            return redirect(url_for('login'))
    # else:
    #     return render_template("studentlogin.html", form=form)
    return render_template("studentlogin.html", form=form)


@application.route('/signup', methods=['GET', 'POST'])  # registration page
def signup():
    reform = register()
    if request.method == 'POST' and reform.validate_on_submit():
        roll = reform.roll.data
        fname = reform.fname.data
        lname = reform.lname.data
        mobile = reform.mob.data
        year = request.form.get("Year")
        sem = request.form.get("semester")
        gen = request.form.get("gender")
        user = reform.user.data
        pwd = reform.pwd.data
        pwd_h = generate_password_hash(pwd)
        # cpwd = reform.cpwd.data
        role = "student"
        cur.execute("insert into student values(%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                    (roll, fname, lname, user, pwd_h, mobile, year, sem, gen))
        cur.execute("insert into roles values(%s,%s,%s)", (roll, user, role))
        conn.commit()
        # print("Registration Successful")
        return redirect(url_for('login'))

    return render_template("reg.html", reform=reform)


@application.route('/forgotpass', methods=['GET', 'POST'])  # forgot password
def forgotpass():
    fform = Forgotpass()
    if request.method == 'POST' and fform.validate_on_submit():
        user = fform.user.data
        # pwd = fform.pwd.data
        cpwd = fform.cpwd.data
        cpwd = generate_password_hash(cpwd)
        cur.execute("select username,password from student where username=%s", user)
        r = cur.fetchone()
        if r is None:
            flash("Username Invalid", "error")
            return redirect(url_for('forgotpass'))
        else:
            # r = dict(r)
            if user == r[0]:
                cur.execute("UPDATE student SET password='%s' where username='%s'" % (cpwd, user))
                conn.commit()
            return redirect(url_for("login"))
    return render_template("forgotpass.html", fform=fform)


""" STUDENT SECTION CODE"""


@application.route('/login/profile')  # User profile
def profile():
    if "user" is None:
            flash("Username Invalid", "error")
            return redirect(url_for('login'))
    elif "user" in session:
        usr = session["fname"]
        rno = session["roll"]
        return render_template("profile.html", usr=usr, rno=rno)
        # else:
        #     return redirect(url_for('login'))


@application.route('/login/profile/stuprof')  # to check the student status
def stuprof():
    if "user" in session:
        us = session["user"]
        cur.execute(
            "select s.id,s.fname,r.username,s.mobile,s.year,s.sem,r.role from student s,roles r "
            "where s.username='%s' and s.username=r.username" % us)
        s = cur.fetchone()
        stid = s[0]
        fname = s[1]
        user = s[2]
        mob = s[3]
        yr = s[4]
        sem = s[5]
        ro = s[6]
        return render_template("stucard.html", nm=fname, roll=stid, us=user, ro=ro, mob=mob, yr=yr, sem=sem)
    else:
        return redirect(url_for('login'))


@application.route('/login/profile/bkissue')  # (student profile) to check the book_issued to the student
def bkissue():
    if "user" in session:
        us = session["user"]
        cur.execute("select * from bir where user='%s'" % us)
        s = cur.fetchall()

        if s is None:
            s = "NO Records Are Available For This User"
        return render_template("bkissue.html", s=s)
    else:
        return redirect(url_for('login'))


@application.route('/login/profile/bktable')  # to display book table in student profile
def bktable1():
    if "user" in session:
        cur.execute("select * from books")
        b = cur.fetchall()
        if b is None:
            b = "No records exists in book table"
        return render_template("bktable.html", b=b)
    else:
        return redirect(url_for('login'))


@application.route('/login/profile/finest')  # to display the fine status of the students
def finest():
    if "user" in session:
        user = session["user"]
        cur.execute("Select * from fine where username='%s'" % user)
        f = cur.fetchall()
        if f is None:
            return redirect(url_for('profile'))
        return render_template("fine.html", f=f)
    else:
        return redirect(url_for('login'))
    

@application.route('/login/profile/speech')  # Speech recognition
def speech():
#     store = SRG.Recognizer()
#     with SRG.Microphone() as s:

#         print("Speak...")

#         audio_input = store.record(s, duration=5)
#         # print("Recording time:",time.strftime("%I:%M:%S"))

#         try:
#             text_output = str(store.recognize_google(audio_input))
#             print("Text converted from audio:")
#             print(text_output)
#             print("Finished!!")

#         #   print("Execution time:",time.strftime("%I:%M:%S"))
#         except Exception as e:
#             print(e)
#             print("Couldn't process the audio input.")
#             return redirect(url_for('profile'))
#         return render_template("profile.html", out=text_output)
    return redirect(url_for("profile"))

@application.route('/login/profile/spsearch', methods=['GET', 'POST'])  # Speech Recognition search
def search():
    if "user" in session:
        if request.method == 'POST':
            data = request.form.get("senddata")
            cur.execute("select * from books where bkid='%s' or bkname='%s' or bkauthor='%s'" % (data, data, data))
            b = cur.fetchall()
            return render_template('bktable.html', b=b)

        return redirect(url_for('profile'))
    else:
        return redirect(url_for('login'))


""" ADMIN SECTION CODE"""


@application.route('/login/admin')
def admin():  # admin page
    if "user" in session:
        if "fname" in session:
            usr = session["fname"]
            return render_template("admin.html", usr=usr)
        else:
            return redirect(url_for('login'))
    else:
        return redirect(url_for('login'))


@application.route('/login/admin/bktable')  # to display book table in admin profile
def bktable():
    if "user" in session:
        cur.execute("select * from books")
        b = cur.fetchall()
        if b is None:
            b = "No records exists in book table"
        return render_template("bktable_ad.html", b=b)
    else:
        return redirect(url_for('login'))


@application.route('/login/admin/sttable')  # to display student table
def sttable():
    if "user" in session:
        cur.execute("select id,fname,lname,username,mobile,year,sem,gender from student")
        s = cur.fetchall()
        if s is None:
            s = "No records exists in student table"
        return render_template("sttable.html", s=s)
    else:
        return redirect(url_for('login'))


@application.route('/login/admin/bkentry', methods=['GET', 'POST'])  # new book entry to database
def bkentry():
    if "user" in session:
        if request.method == 'POST':
            bk_id = int(request.form["inputBookID"])
            bk_name = request.form["inputBookName"]
            bk_author = request.form["inputAuthor"]
            bk_edition = int(request.form["inputEdition"])
            bk_publication = request.form["inputPublication"]
            bk_genre = request.form["inputGenre"]
            bk_status = request.form["inputStatus"]
            cur.execute("select bkid from books where bkid=%s", bk_id)
            r = cur.fetchone()
            print(r, bk_id)
            if r is not None: # if the given bookid is there in database
                r1 = r[0]
                print(r1)
                if r1 == bk_id:
                    flash("Book ID already exist","danger")
                    return redirect(url_for('bkentry'))
            cur.execute("select * from books where bkname=%s", bk_name.lower())
            details = cur.fetchone()
            if details is not None:
                bid,bname,bauthor,bedition,bpublication,bgenre,bstatus = details    
                    
                if bname.lower() ==bk_name.lower() and bauthor.lower() == bk_author.lower() and bedition == bk_edition and bpublication.lower() == bk_publication.lower() and bgenre == bk_genre and r is None:
                    flash("Book already exists with different Book ID","danger")
                    return redirect(url_for('bkentry'))
                else:
                    cur.execute("insert into books values(%s,%s,%s,%s,%s,%s,%s)",
                            (bk_id, bk_name.lower(), bk_author.lower(), bk_edition, bk_publication.lower(), bk_genre, bk_status))
                    conn.commit()
            else:
                    cur.execute("insert into books values(%s,%s,%s,%s,%s,%s,%s)",
                            (bk_id, bk_name, bk_author, bk_edition, bk_publication, bk_genre, bk_status))
                    conn.commit()
                # return render_template("bookentry.html")
        return render_template("bookentry.html")
    else:
        return redirect(url_for('login'))


@application.route('/login/admin/bkissue/')  # bookissue /return page
def bissue():
    if "user" in session:
        return render_template("bookissue.html")
    else:
        return redirect(url_for('login'))


@application.route('/login/admin/bkissue/<string:buttontype>', methods=['POST'])  # book issue/return functionality
def bkissuer(buttontype):
    if "user" in session:
        if request.method == 'POST':
            bkid = int(request.form.get("bookid"))
            stid = int(request.form.get("stid"))
            cur.execute("select username from student where id=%d" % stid)
            if cur.fetchone() is not None:
                cur.execute("select username from student where id=%d" % stid)
                usr = cur.fetchone()
            else:
                flash("User doesn't exist","danger")
                return redirect(url_for('bissue'))
            cur.execute("select bkstatus from books where bkid=%d" % bkid)
            if cur.fetchone() is not None:
                cur.execute("select bkstatus from books where bkid=%d" % bkid)
                bst = cur.fetchone()
                bst = ''.join(map("".join, bst))   # converting the tuple to string
            else:
                flash("The Specified BookID doesn't exist","danger")
                return redirect(url_for('bissue'))        
            
              
            # print(buttontype)
            if buttontype == "Issue":
                isdt = request.form.get('trip-start')
                rtdt = request.form.get('trip-end')
                cur.execute("select bkname from books where bkid=%d" % bkid)
                bkname = cur.fetchone()    # bkname is a tuple containing the bkname
                # print(bkname)
                bkname = ''.join(map("".join, bkname))  # converting the tuple to string
                # print(bkname, type(bkname))
                if bst == "Available":
                    cur.execute('insert into bir values(%s,%s,%s,%s,%s,%s,%s)',
                                (usr, stid, bkid, bkname, isdt, rtdt, 'Issued'))
                    conn.commit()
                    cur.execute('update books set bkstatus="Unavailable" where bkid=%d' % bkid)
                    conn.commit()
                    flash("THE BOOK IS ISSUED", "error")
                else:
                    flash("THE BOOK YOU ARE GOING TO ISSUE IS CURRENTLY UNAVAILABLE", "error")
                    return redirect(url_for('bissue'))
                return redirect(url_for('bissue'))

            if buttontype == "Return":

                cur.execute("select doi from bir where id=%d" % stid)
                issue_tup = cur.fetchall()
                isdt=issue_tup[-1]
                print("last issued date: ", isdt)
                print("type(last issued date): ",type(isdt))
                tup_lis=list(isdt)
                print(tup_lis, type(tup_lis))
                #temp= ''.join(isdt)
                #print(temp, type(temp))
                # print("Issue date :{}\n Type(Issue Date) :{}".format(isdt, type(isdt)))
                rtdt = request.form.get('trip-end')
                # print("Return date(FORM) :{}\n Type(Return Date(Form)) :{}".format(rtdt, type(rtdt)))
                rtdt = datetime.strptime(rtdt, '%Y-%m-%d').date()  # converting the string obj(rtdt) to datetime.date object
                #temp = datetime.strptime(temp, '%Y-%m-%d').date()
                # print("after conversion ")
                # print(type(rtdt))
                cur.execute('select books.bkname,bir.dor from books,bir where books.bkid=bir.bkid and bir.bkid=%d'
                            % bkid)
                tup=cur.fetchall()
                #print(tup)
                #print("********")
                bkname, rt_dt = tup[-1]
                # print(bkname,rt_dt)
                # print("----------")
                # print("Return date(Table) :{}\n Type(Return Date(Table)) :{}".format(rt_dt, type(rt_dt)))
                if bst == "Unavailable":
                    cur.execute('update bir set dor="%s",return_status="Returned" where doi="%s" and bkid=%d' % (rtdt,tup_lis[0], bkid))
                    conn.commit()
                    cur.execute('update books set bkstatus="Available" where bkid=%d' % bkid)
                    conn.commit()
                    flash("THE BOOK IS RETURNED", "error")
                    def day(s):

                        s = str(s)
                        s = s.rstrip(' 00:00:00')
                        print("date in string : ",s)
                        year, month, day_s = s.split("-")
                        print(date(int(year), int(month), int(day_s)))
                        print("||||||||||||||")
                        return date(int(year), int(month), int(day_s))

                    def days(rtdt, rt_dt):
                        print("table return date:" ,rt_dt)
                        print("form return date:" ,rtdt)
                        print((day(rtdt) - day(rt_dt)).days)
                        return (day(rtdt) - day(rt_dt)).days

                    Days = days(rtdt, rt_dt)
                    print("difference = ",Days)
                    if Days == 0:
                        cur.execute('insert into fine values(%s,%s,%s,%s,%s,%s,%s,%s)',
                                    (stid, usr, bkid, bkname, isdt, rtdt, 0, "NuLL"))
                        conn.commit()

                    elif Days > 0:
                        cur.execute('insert into fine values(%s,%s,%s,%s,%s,%s,%s,%s)',
                                    (stid, usr, bkid, bkname, isdt, rtdt, (Days * 2), "NOT PAID"))
                        conn.commit()

                    else:
                        cur.execute('insert into fine values(%s,%s,%s,%s,%s,%s,%s,%s)',
                                    (stid, usr, bkid, bkname, isdt, rtdt, 0, "NILL"))
                        conn.commit()
                else:
                    flash("THE BOOK YOU ARE RETURNING IS ALREADY AVAILABLE", "error")
                    return redirect(url_for('bissue'))
                return redirect(url_for('bissue'))
    else:
        return redirect(url_for('login'))


@application.route('/login/admin/bk', methods=['GET', 'POST'])  # Speech Recognition search in admin page
def bk():
    if "user" in session:
        if request.method == 'POST':
            data = request.form.get("senddata")
            cur.execute("select * from books where bkid=%s or bkname=%s or bkauthor=%s", (data, data, data))
            b = cur.fetchall()
            return render_template('bktable_ad.html', b=b)
        # else:
        #     return redirect(url_for('admin'))
        return redirect(url_for('admin'))
    else:
        return redirect(url_for('login'))


@application.route('/login/admin/review') # review in admin page
def review():
    if "user" in session:
        cur.execute("select * from review")
        review_feed = cur.fetchall()
        if review_feed is None:
            return "No Review is Given"
        return render_template('review.html', review=review_feed)
    else:
        return redirect(url_for('login'))


@application.route("/login/admin/rolech", methods=["GET", "POST"])  # to change the role of students
def rolech():
    if "user" in session:
        if request.method == "POST":
            stid = request.form.get("id")
            rol = (request.form.get("role"))
            
            # rid = request.form.get("id")
            cur.execute("select id from student where id=%s", int(stid))
            rid = cur.fetchone()
            if rid is not None:
                rec_id=rid[0]
                s=str(rec_id)
                #r = ''.join(map("".join,s))
                #print(rid,type(rid),r, type(r),stid, type(stid))
                if s != stid:
                    flash("Roll Number Exists", "error")
                else:
                    cur.execute("update roles set role='%s' where roles.id=%d" % (rol, int(stid)))
                    conn.commit()
                    flash("Role Changed", "error")
            else:
                flash("Roll Number Invalid", "error")
        return render_template("rolechange.html")
    else:
        return redirect(url_for('login'))


@application.route('/login/admin/fine')  # to display the fine of all students
def fineall():
    if "user" in session:
        cur.execute("select * from fine")
        f = cur.fetchall()
        if f is None:
            f = "No records exists in book table"
        return render_template('fineall.html', f=f)
    else:
        return redirect(url_for('login'))


@application.route('/login/admin/speech')  # Speech Recognition
def speechad():
    # store = SRG.Recognizer()
    # with SRG.Microphone() as s:

    #     print("Speak...")

    #     audio_input = store.record(s, duration=5)
    #     # print("Recording time:",time.strftime("%I:%M:%S"))

    #     try:
    #         text_output = str(store.recognize_google(audio_input))
    #         print("Text converted from audio:")
    #         print(text_output)
    #         print("Finished!!")

    #     #   print("Execution time:",time.strftime("%I:%M:%S"))
    #     except Exception as e:
    #         print(e)
    #         print("Couldn't process the audio input.")
    # return render_template("admin.html", out=text_output)
    return redirect(url_for("admin"))

@application.route('/login/admin/fineupdate', methods=["GET", "POST"]) #fine status update
def statUpdate():
    if "user" in session:
        if request.method == "POST":
            stid = request.form.get("id")
            status = request.form.get("status")
            cur.execute("update fine set fine_status='%s' where fine.id=%d" % (status, int(stid)))
            conn.commit()
            #rid = request.form.get("id")
            cur.execute("select id from student where id=%d" % int(stid))
            rid = cur.fetchone()
            if rid is not None:
                rec_id=rid[0]
                s=str(rec_id)
                #print(s, type(s))
                #r = ''.join(map("".join,s))
                #print(rid,type(rid),r, type(r),stid, type(stid))
                if s != stid:
                    flash("Roll Number Exists", "error")
                else:
                    cur.execute("update fine set fine_status='%s' where fine.id=%d" % (status, int(stid)))
                    conn.commit()
                    flash("Fine  Status Updated", "error")
            # cur.execute("select id from student where id=%s", rid)
            # r = cur.fetchone()
            else:
                flash("Roll Number Invalid", "error")
        return render_template("fine_st_up.html")
    else:
        return redirect(url_for('login'))

"""
LOGOUT SECTION

"""


@application.route('/logout')
def logout():
    if "user" in session:
        if session["role"] == "admin":
            session.pop("user", None)
            session.pop("fname", None)
            session.pop("role", None)
            return redirect(url_for('home'))
        else:
            session.pop("user", None)
            session.pop("fname", None)
            session.pop("roll", None)
            session.pop("role", None)
            return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))


if __name__ == "__main__":
    application.run(debug=True)

import variables as v
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from sqlalchemy import and_, or_, text, desc, asc

from flask_login import UserMixin


@v.login_manager.user_loader
def load_user(user_id):
    """Get user by id.

    Arguments:
        user_id {int} -- user identificator.

    Returns:
        User -- User with that id.
    """
    return User.query.get(user_id)


def load_experiment(exp_id):
    """Get experiment by id.

    Arguments:
        exp_id {int} -- experiment identificator.

    Returns:
        Experiment -- Experiment with that id.
    """
    return Experiment.query.get(exp_id)


def get_experiments(idu):
    """Get all experiments from an user.

    Arguments:
        idu {int} -- user identificator.

    Returns:
        experiments list -- all experiments from user with that id.
    """
    listexp = Experiment.query.filter(Experiment.idu == idu).all()
    for i in listexp:
        i.starttime = datetime.fromtimestamp(i.starttime)\
            .strftime("%d/%m/%Y - %H:%M:%S")
        if i.endtime is not None:
            i.endtime = datetime.fromtimestamp(i.endtime)\
                .strftime("%d/%m/%Y - %H:%M:%S")
    return listexp


def get_algorithms_type():
    sql = text('SELECT DISTINCT alg_typ FROM algorithms')
    result = v.db.engine.execute(sql)
    types = [(row[0], row[0]) for row in result if row[0] != "Mixed"]
    return types


# def get_similar_algorithms(alg_name):
#     """Get algorithm that can be base estimator
    
#     Arguments:
#         alg_name {str} -- Name of the algorithm
    
#     Returns:
#         list of lists -- all similar algorithms
#     """
#     alg = get_algorithm_by_name(alg_name)
#     if alg.lib != "meka":
#         cond = Algorithm.lib == alg.lib
#     else:
#         cond = Algorithm.lib == "weka"
#         if alg.alg_typ == "MultiClassification":
#             cond = and_(cond, or_(Algorithm.alg_typ == "Classification",
#                                   Algorithm.alg_typ == "Mixed"))
#         else:
#             cond = and_(cond, or_(Algorithm.alg_typ == "Regression",
#                                   Algorithm.alg_typ == "Mixed"))
#     if alg.alg_typ != "Mixed" and alg.lib != "meka":
#         cond = and_(cond, Algorithm.alg_typ == alg.alg_typ)
#     elif alg.lib != "meka":
#         cond = and_(cond, or_(Algorithm.alg_typ == "Classification",
#                               Algorithm.alg_typ == "Regression"))
#     algorithms = Algorithm.query.filter(cond).all()
#     return algorithms


def get_similar_algorithms(alg_name, exp_typ):
    alg = get_algorithm_by_name(alg_name)
    if alg.lib == "meka":
        cond = and_(Algorithm.lib == "weka",
                    or_(Algorithm.alg_typ == "Classification",
                        Algorithm.alg_typ == "Mixed"))
    else:
        cond = Algorithm.lib == alg.lib
        subcond = Algorithm.alg_typ == exp_typ
        if exp_typ in ["Classification", "Regression"]:
            subcond = or_(subcond, Algorithm.alg_typ == "Mixed")
        cond = and_(cond, subcond)
    algorithms = Algorithm.query.filter(cond).all()
    return algorithms


def get_algorithms(alg_typ):
    """Get algorithms by type.

    Arguments:
        alg_typ {string} -- algorithm type.

    Returns:
        algorithm list -- all algorithm of that type.
    """
    cond = Algorithm.alg_typ == alg_typ
    if alg_typ in ["Classification", "Regression"]:
        cond = or_(cond, Algorithm.alg_typ == "Mixed")
    return Algorithm.query.filter(cond).order_by(asc(Algorithm.web_name)).all()


def get_algorithm_by_name(name):
    """Get an algorithm by name.

    Arguments:
        name {string} -- name of the algorithm.

    Returns:
        Algorithm -- Algorithm with that name.
    """
    return Algorithm.query\
        .filter(Algorithm.alg_name == name).first()


def get_filter_by_name(name):
    """Get an algorfilterithm by name.

    Arguments:
        name {string} -- name of the filter.

    Returns:
        Filter -- Filter with that name.
    """
    return Filter.query\
        .filter(Filter.filter_name == name).first()


def get_compatible_filters(lib, typ=None):
    """Get an filter by .

    Arguments:
        name {string} -- name of the algorithm.

    Returns:
        Algorithm -- Algorithm with that name.
    """
    cond = Filter.lib == lib
    if typ is not None:
        cond = and_(cond, Filter.typ == typ)
    return Filter.query\
        .filter(cond).all()

def delete_experiment(id):
    Experiment.query.filter_by(id=id).delete()
    v.db.session.commit()

class User(v.db.Model, UserMixin):

    __tablename__ = 'users'

    id = v.db.Column(v.db.Integer, primary_key=True)
    email = v.db.Column(v.db.String(64), unique=True, index=True)
    username = v.db.Column(v.db.String(64), unique=True, index=True)
    password_hash = v.db.Column(v.db.String(128))
    activated = v.db.Column(v.db.Boolean, nullable=False, default = False)

    def __init__(self, email, username, password):
        """User constructor

        Arguments:
            email {string} -- User's email
            username {string} -- User name identifer
            password {string} -- User's password
        """
        self.email = email
        self.username = username
        self.password_hash = generate_password_hash(password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        """Compare input password with current password

        Arguments:
            password {string} -- Input password

        Returns:
            boolean -- True if both password match, instead False
        """
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        """Representation

        Returns:
            str -- representation
        """
        return f"Email: {self.email} Username: {self.username}"

    def __str__(self):
        """to string

        Returns:
            str -- information string
        """
        return self.__repr__() + f" Email: {self.email}"

    def to_dict(self):
        """Object to dict

        Returns:
            dict -- dict with key and value from the object.
        """
        return {"id": self.id,
                "email": self.email,
                "username": self.username,
                "password": self.password_hash}


class Algorithm(v.db.Model):

    __tablename__ = 'algorithms'

    id = v.db.Column(v.db.Integer, primary_key=True)
    alg_name = v.db.Column(v.db.String(64), unique=True)
    web_name = v.db.Column(v.db.String(64))
    alg_typ = v.db.Column(v.db.String(64))
    config = v.db.Column(v.db.Text)
    lib = v.db.Column(v.db.String(64))

    def __init__(self, alg_name, web_name, alg_typ, config, lib):
        """Algorithm constructor.

        Arguments:
            alg_name {str} -- algorithm name.
            web_name {str} -- algorithm web name.
            alg_typ {str} -- algorithm type
            config {str} -- json with algorithm configuration.
            lib {str} -- sklearn or weka.
        """

        self.alg_name = alg_name
        self.web_name = web_name
        self.alg_typ = alg_typ
        self.config = config
        self.lib = lib

    def to_dict(self):
        """Algorithm to dict

        Returns:
            dict -- dict with keys and values from Algorithm Object.
        """
        return {"id": self.id,
                "alg_name": self.alg_name,
                "web_name": self.web_name,
                "alg_typ": self.alg_typ,
                "config": self.config,
                "lib": self.lib}


class Filter(v.db.Model):

    __tablename__ = "filters"

    id = v.db.Column(v.db.Integer, primary_key=True)
    filter_name = v.db.Column(v.db.String(64), unique=True)
    web_name = v.db.Column(v.db.String(64))
    filter_typ = v.db.Column(v.db.String(64))
    config = v.db.Column(v.db.Text)
    lib = v.db.Column(v.db.String(64))

    def __init__(self, filter_name, web_name, filter_typ, config, lib):
        """Algorithm constructor.

        Arguments:
            filter_name {str} -- filter name.
            web_name {str} -- filter web name.
            filter_typ {str} -- filter type
            config {str} -- json with filter configuration.
            lib {str} -- sklearn or weka.
        """

        self.filter_name = filter_name
        self.web_name = web_name
        self.filter_typ = filter_typ
        self.config = config
        self.lib = lib

    def to_dict(self):
        """Algorithm to dict

        Returns:
            dict -- dict with keys and values from Filter Object.
        """
        return {"id": self.id,
                "filter_name": self.filter_name,
                "web_name": self.web_name,
                "filter_typ": self.filter_typ,
                "config": self.config,
                "lib": self.lib}


class Experiment(v.db.Model):

    __tablename__ = 'experiments'

    id = v.db.Column(v.db.Integer, primary_key=True)
    idu = v.db.Column(
        v.db.Integer,
        v.db.ForeignKey('users.id'),
    )
    alg_name = v.db.Column(
        v.db.String(64),
        v.db.ForeignKey('algorithms.alg_name'),
    )
    alg_config = v.db.Column(v.db.Text)
    exp_config = v.db.Column(v.db.Text)
    filter_name = v.db.Column(
        v.db.String(64),
        v.db.ForeignKey('filters.filter_name'),
        nullable=True
    )
    filter_config = v.db.Column(v.db.Text, nullable=True)
    data = v.db.Column(v.db.String(128))
    result = v.db.Column(v.db.Text, nullable=True)
    starttime = v.db.Column(v.db.Integer)
    endtime = v.db.Column(v.db.Integer, nullable=True)
    state = v.db.Column(v.db.Integer)

    def __init__(self, idu, alg_name, alg_config, exp_config,
                 filter_name, filter_config, data, result,
                 starttime, endtime, state):
        """Experiment constructor.

        Arguments:
            idu {integer} -- User who lauch experiment.
            alg_name {string} -- Experiment's algorithm name.
            alg_config {string} -- Experiment's algorithm configuration.
            data {string} -- Experiment data.
            result {string} -- Experiment result.
            starttime {integer} -- Experiment start timestamp.
            endtime {integer} -- Experiment end timestamp.
            state {integer} -- State of experiment.
                               (0. Execution, 1. completed, 2. Error)
        """
        self.idu = idu
        self.alg_name = alg_name
        self.alg_config = alg_config
        self.exp_config = exp_config
        self.filter_name = filter_name
        self.filter_config = filter_config
        self.data = data
        self.result = result
        self.starttime = starttime
        self.endtime = endtime
        self.state = state

    def to_dict(self):
        """Experiment to dict

        Returns:
            dict -- dict with keys and values from Experiment Object.
        """
        filter_ = get_filter_by_name(self.filter_name)
        if filter_ is not None:
            filter_ = filter_.to_dict()
        return {"id": self.id, "idu": self.idu,
                "alg": get_algorithm_by_name(self.alg_name).to_dict(),
                "alg_config": self.alg_config, "exp_config": self.exp_config,
                "filter": filter_,
                "filter_config": self.filter_config,
                "data": self.data,
                "result": self.result, "starttime": self.starttime,
                "endtime": self.endtime}

    def web_name(self):
        return get_algorithm_by_name(self.alg_name).web_name

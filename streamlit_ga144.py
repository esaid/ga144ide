import requests
import bibliotheque_create
import json
import os
import time
import glob
import serial.tools.list_ports
import streamlit as st
import streamlit_authenticator as stauth
import database
from streamlit_ace import st_ace
from streamlit_lottie import st_lottie
from streamlit_option_menu import option_menu
from itertools import cycle
from contextlib import redirect_stdout, redirect_stderr
import io
import sys
import subprocess
import traceback
from pathlib import Path

# élargir la page
st.set_page_config(layout="wide", initial_sidebar_state="collapsed")
path_avatar_drive = 'avatar'
if "avatar" not in st.session_state:
    st.session_state["avatar"] = ''

if 'login' not in st.session_state:
    st.session_state["login"] = False
# read datas from user.database
d = database.fetch_all(database.db_user)  # all items user database
next_key = database.next_key(d)

list_usernames = database.filter_database(d, "username")  # all values username
list_name = database.filter_database(d, "name")  # all values name
list_email = database.filter_database(d, "email")  # all values email
list_passwords = database.filter_database(d, "password")  # values password
list_avatar = database.filter_database(d, 'avatar')  # values avatar
list_emails_prehautorized = ["emmanuel.said@gmail.com"]
list_value_cookies = [30, "random_signature_key", "random_cookie_name"]
# read list_passwords ( hashed values)
# list_name, list_usernames, list_passwords = database.read_hashed_passwords('hashed_pwd.plk')

config = database.autentificator_list_dict(list_usernames, list_email, list_name, list_passwords,
                                           list_emails_prehautorized, list_value_cookies)
authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)

name, authentication_status, username = authenticator.login('GA144', 'main')

placeholder = st.empty()
with placeholder.container():
    if authentication_status:
        st.session_state["login"] = True
        st.session_state["avatar"] = list_avatar[list_usernames.index(f"{username}")]
        st.image(database.get_file_drive(database.avatar_drive, st.session_state["avatar"]), width=70,
                 caption=f"Welcome {username}")
        authenticator.logout('Logout', 'main')
        time.sleep(0.1)
    elif authentication_status == False:
        st.error('Username/password is incorrect')
    elif authentication_status == None:
        st.warning('Please enter your username and password')
    if st.session_state["login"] == False:
        try:
            st.session_state["avatar"] = st.selectbox("my avatar 👇", database.list_files(database.avatar_drive))
            st.image(database.get_file_drive(database.avatar_drive, st.session_state["avatar"]), width=70)
            if authenticator.register_user('Register user', preauthorization=False):
                st.success('User registered successfully')
                # st.write(config) # recueration des valeurs register_user
                last_username = list(config['credentials']['usernames'])[-1]  # last register
                last_name = config['credentials']['usernames'][last_username]['name']
                last_email = config['credentials']['usernames'][last_username]['email']
                last_password = config['credentials']['usernames'][last_username]['password']
                dict_db_user = {
                    'name': last_name,
                    'username': last_username,
                    'email': last_email,
                    'avatar': st.session_state["avatar"],
                    'password': last_password,
                    'key': str(next_key)
                }
                # st.write(dict_db_user)
                # st.write(last_username, last_name, last_email, last_password)
                database.put_database(database.db_user, dict_db_user)  # ecriture dans datatbase user
                time.sleep(0.1)
                st.session_state["login"] = True
                placeholder.empty()
        except Exception as e:
            st.error(e)

GPIO = ('600', '500', '217', '317', '417', '517', '715')
Analog = ('117', '617', '717', '713', '709')

CLK = ('300', '001', '701')
DATA = ('300', '001', '701')
Internal = (
    '002', '003', '004', '005', '006', '010', '011', '012', '013', '014', '015', '016', '017', '101', '102', '103',
    '104', '105', '106', '107',
    '108', '109', '110', '111', '112', '113', '114', '115', '116', '201', '202', '203', '204', '205', '206', '207',
    '208', '209', '210', '211', '212',
    '213', '214', '215', '216', '300', '301', '302', '303', '304', '305', '306', '307', '308', '309', '310', '311',
    '312', '313', '314', '315', '316',
    '400', '401', '402', '403', '404', '405', '406', '407', '408', '409', '410', '411', '412', '413', '414', '415',
    '416',
    '501', '502', '503', '504', '505', '506', '507', '508', '509', '510', '511', '512', '513', '514', '515', '516',
    '601', '602', '603', '604', '605', '606', '607', '608', '609', '610', '611', '612', '613', '614', '615', '616',
    '700', '701', '702', '703', '704', '706', '707', '708', '710', '711', '712', '714', '716')


def bar_progression(progress, t):
    percent_complete = 0
    my_bar = st.progress(percent_complete)
    while percent_complete < 100:
        percent_complete += progress
        time.sleep(t)
        my_bar.progress(percent_complete)
    my_bar.empty()


def find_fonction_node(node_):
    if node_ in GPIO:
        return 'GPIO'
    if node_ in Analog:
        return 'Analog'
    if node_ in CLK:
        return 'CLK'
    if node_ in DATA:
        return 'DATA'
    if node_ in Internal:
        return 'Internal'


# lottie url file
def load_lottieurl(url: str):
    r = requests.get(url)
    if r.status_code != 200:
        return None
    return r.json()


def load_lottiefile(filepath: str):
    with open(filepath, "r") as f:
        return json.load(f)


def read_file(name_file):
    with open(name_file, "r") as file_:
        return file_.read()


def write_file(name_file, content_):
    with open(name_file, "wb") as file_:
        file_.write(content_)
        file_.close()


def concatenation_in_onefile(new_file, list_files):
    with open(new_file, "w") as new_file:
        for name in list_files:
            with open(name) as f:
                for line in f:
                    new_file.write(line)
                new_file.write("\n")


def file_in_folder():
    directory = "\n\r".join(str(st.session_state['folder_project']).split())
    os.chdir(directory)  # path projet
    return sorted(glob.glob("*.node"))


def is_file_exist(file_):
    folder = file_in_folder()
    return file_ + '.node' in folder


def select_folder_streamlit():
    streamlit_folder = "\n\r".join(str(st.session_state['folder_streamlit']).split())
    # st.write(f"--> folder streamlit {streamlit_folder}")
    os.chdir(streamlit_folder)  # path projet
    time.sleep(0.1)


def select_Folder_principal():
    if os.path.exists(master_folder):
        st.session_state['folder_principal'] = master_folder
        st.success("Folder validated ")
        time.sleep(0.1)
    else:
        st.warning('error Folder not found...')
        st.stop()


def file_exist(file_):
    return os.path.exists(file_) and os.stat(file_).st_size == 0


def select_folder_project():
    project_folder = "\n\r".join(str(st.session_state['folder_project']).split())
    # st.write(project_folder)
    os.chdir(project_folder)  # path projet


def view_code_node():
    code_ = st.session_state['code']
    # affiche le code dans editeur ace
    code_edit = st_ace(value=code_, language='forth', theme='cobalt', font_size=25, auto_update=False, key='view')
    # node_file = f"{code_editeur.title().split()[1]}.node"  # ['Node','117']  '117.node'
    # st.session_state['file_node'] = node_file
    st.session_state['code'] = code_edit
    return code_edit


if st.session_state["login"] == True:
    # gestion projet
    if 'projet' not in st.session_state:
        st.session_state['projet'] = False

    if 'name_projet' not in st.session_state:
        st.session_state['name_projet'] = ""

    # gestion repertoire projet
    if 'folder_project' not in st.session_state:
        st.session_state['folder_project'] = ''
    # gestion repertoire streamlit
    if 'folder_streamlit' not in st.session_state:
        # initialisation par defaut
        st.session_state['folder_streamlit'] = os.path.dirname(__file__)  # sauvegarde repertoire streamlit

    if 'folder_principal' not in st.session_state:
        st.session_state['folder_principal'] = st.session_state['folder_streamlit']

    if 'menu_gestion_projet' not in st.session_state:
        st.session_state['menu_gestion_projet'] = False

    # gestion Lib

    if 'folder_lib' not in st.session_state:
        st.session_state['folder_lib'] = st.session_state['folder_streamlit'] + "/lib/"

    if 'code' not in st.session_state:
        st.session_state['code'] = ''

    if 'file_node' not in st.session_state:
        st.session_state['file_node'] = ''

    if 'compilation_file' not in st.session_state:
        st.session_state['compilation_file'] = ''

    if 'send' not in st.session_state:
        st.session_state['send'] = False

    if 'lib_update' not in st.session_state:
        st.session_state['lib_update'] = False

    if 'serial_port' not in st.session_state:
        st.session_state['serial_port'] = ''
    if 'loaded' not in st.session_state:
        st.session_state['loaded'] = False

    select_folder_streamlit()
    # st.write(st.session_state['folder_lib'])
    # charger animation cpu
    cpu_file = "cpu.json"
    # dir_cpu_file = f"{st.session_state['folder_streamlit']}{cpu_file}"

    # lottie_cpu = load_lottiefile(cpu_file)
    lottie_cpu = database.get_file_drive_json(database.lotties_drive, cpu_file)

    # charger animation ecriture code informatique
    lottie_urlGA144 = "https://assets9.lottiefiles.com/packages/lf20_xafe7wbh.json"
    lottie_jsonGA144 = load_lottieurl(lottie_urlGA144)

    # titre avec style css html
    original_title = '<p style="font-family:Courier; color:Green; font-size: 40px;">GA144 FORTH</p>'
    st.markdown(original_title, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    with col3:
        # affichage repertoire fichiers du projet si exisant
        if st.session_state['projet'] is True:
            st.metric("--- Nodes ---", "144", f"{len(file_in_folder()) - 1} nodes")
            st.write('\n')
            project_font = f"""<style>p.a {{ font: bold 15px Courier;}}</style><p class="a">  Project :: {st.session_state['name_projet']}</p>"""
            st.markdown(project_font, unsafe_allow_html=True)
            file_project_font = f"""<style>p.a {{ font: bold 15px Courier;}}</style><p class="a">{', '.join(file_in_folder())}</p>"""
            st.markdown(file_project_font, unsafe_allow_html=True)

    # afficher  animation cpu
    with st.spinner(text="GA144"):
        st_lottie(lottie_jsonGA144, height=150, key="loading_gif")
    # afficher animation cpu et menu vertical
    with st.sidebar:
        selected_vertical_menu = option_menu("Main Menu", ["Home", 'Setting-communication', 'About'],
                                             icons=['house', 'motherboard', 'question'],
                                             menu_icon="cast",
                                             default_index=0)
        # selection node par type et numero node

        node_type = st.selectbox(
            'Node Type Selection :',
            ('NODE', 'GPIO', 'Analog_In', 'Analog_Out', 'CLK', 'DATA', 'Internal'))

        list_node = ''
        if node_type == 'GPIO':
            list_node = GPIO
        if node_type == 'Analog_In':
            list_node = Analog
        if node_type == 'Analog_Out':
            list_node = Analog
        if node_type == 'CLK':
            list_node = CLK
        if node_type == 'DATA':
            list_node = DATA
        if node_type == 'Internal':
            list_node = Internal

        node = st.selectbox('Node', list_node)
        st.write('NODE Type selected:', node_type)
        st.write('NODE selected:', node)
        st_lottie(lottie_cpu, speed=1, height=150)
        selected_horizontal_cpu = option_menu(None, ["", "Compilation", "Send", "Lib-Update"],
                                              icons=['', 'gear', 'caret-down-square-fill', 'caret-down-square'],
                                              menu_icon="cast", default_index=0, orientation="horizontal",
                                              styles={
                                                  "container": {"padding": "0!important",
                                                                "background-color": "#fafafa"},
                                                  "icon": {"color": "orange", "font-size": "18px"},
                                                  "nav-link": {"font-size": "18px", "text-align": "left",
                                                               "margin": "2px",
                                                               "--hover-color": "#eee"},
                                                  "nav-link-selected": {"background-color": "green"},
                                              }
                                              )

        if selected_horizontal_cpu == "Compilation":
            st.info(f"compilation {st.session_state['name_projet']}", icon="ℹ️")
            bar_progression(10, 0.1)
            # save name_projet.Cga  (Compilationga)
            l = file_in_folder()
            l = l[-1:] + l[:-1]  # init.node premier element pour gerer  require
            st.write(st.session_state['name_projet'])
            st.session_state['compilation_file'] = st.session_state['name_projet'] + '.Cga'
            concatenation_in_onefile(st.session_state['compilation_file'], l)
            code = read_file(st.session_state['compilation_file'])
            # new code
            file_ga_ = st.session_state['compilation_file'] + '_'
            directoryBibliotheque = st.session_state['folder_lib']
            bibliotheque_create.generation_code(code, directoryBibliotheque, file_ga_)
            st.stop()

        if selected_horizontal_cpu == "Send":
            st.info(f"Send program to board !{st.session_state['serial_port']}", icon="ℹ️")
            bar_progression(10, 0.1)
            st.session_state['send'] = True
            st.stop()
        if selected_horizontal_cpu == "Lib-Update":
            st.info(f"Update Lib Files ", icon="ℹ️")
            Path(st.session_state['folder_lib']).mkdir(parents=True, exist_ok=True)  # creation Floder lib
            os.chdir(st.session_state['folder_lib'])
            list_lib = database.list_files(database.lib_drive)
            st.write(list_lib)
            for l in list_lib:
                file_content = database.get_file_drive(database.lib_drive, l)
                write_file(l, file_content)
                st.write(f"Write file {l}\n")
            st.info(f"Done ", icon="ℹ️")
            select_folder_project()

    col1, col2 = st.columns(2)

    # col2 creation ou col1 ouvrir un projet le fichier ini.node ( pour connaitre le repertoire )
    # charger  projet

    with col1:
        phcol1 = st.empty()
        with phcol1.container():
            # si pas de projet , on sélectionne le repertoire et fichier ini.node
            if st.session_state['projet'] is False:
                st.header('Load Project :')
                select_projet = st.file_uploader("Choose a file init.node in project folder ", type=['node'])
                st.warning('Please select a file init.node')
                if select_projet:
                    if select_projet.name == 'init.node':
                        st.info("file init.node' selected")

                        st.session_state['projet'] = True

                        directory_project = select_projet.getvalue().decode('utf-8').split('\n')[0][
                                            2:]  # 1ere ligne , chemin du projet
                        st.session_state['folder_project'] = directory_project.strip()
                        st.write(directory_project)
                        # name_projet = directory_project[directory_project.rindex('/') + 1:]
                        name_projet = Path(directory_project).stem.strip()
                        st.write(name_projet)
                        st.session_state['name_projet'] = name_projet
                        # st.write(name_projet)
                        # st.write(file_in_folder())
                        time.sleep(0.1)
                        phcol1.empty()

    # creer projet
    with col2:
        phcol2 = st.empty()
        with phcol2.container():
            # si pas de projet  , creation du projet
            if st.session_state['projet'] is False:
                st.header('Create Project :')
                name_projet = st.text_input('Name Project :  👇')  # nom du projet
                if not name_projet:  # gere si on a bien rentre un nom de projet
                    st.warning('Please input a name  project')
                    st.stop()
                master_folder = st.text_input(label='Input Master Folder for projects :  📗   ',
                                              help=st.session_state['folder_principal'])
                if not master_folder:
                    st.warning('Please input a Folder')
                    st.stop()
                select_Folder_principal()
                st.write(f"Current working directory: {st.session_state['folder_streamlit']}")  # folder courant

                st.session_state['projet'] = True
                st.session_state['name_projet'] = name_projet
                st.success(f"Thank you for inputting a name. {st.session_state['projet']}")
                # st.session_state['folder_project'] = os.path.join(st.session_state['folder_principal'], name_projet)  # chemin repertoire du projet
                st.session_state['folder_project'] = Path(f"{st.session_state['folder_principal']}/{name_projet}")
                try:
                    os.mkdir(st.session_state['folder_project'])  # creation repertoire , avec nom de projet
                except OSError as errordirectory:
                    st.error(f'This is an error  {errordirectory}', icon="🚨")
                    st.stop()
                select_folder_project()
                st.info(f'Create init.node file in {name_projet}', icon="ℹ️")
                init_text = f"\ {st.session_state['folder_project']}\n"  #
                # creation du fichier ini.node
                with open('init.node', "w") as f:
                    f.write(init_text)  # save code init file
                time.sleep(0.1)
                phcol1.empty()
                phcol2.empty()
    # menu horizontal
    selected_horizontal = option_menu(None, ["Home", "New", "Load", 'Save', 'Restart'],
                                      icons=['house', 'plus-square', 'bi-file-earmark-arrow-down-fill',
                                             'bi-file-earmark-arrow-up-fill',
                                             ],
                                      menu_icon="cast", default_index=0, orientation="horizontal",
                                      styles={
                                          "container": {"padding": "0!important", "background-color": "#fafafa"},
                                          "icon": {"color": "orange", "font-size": "25px"},
                                          "nav-link": {"font-size": "25px", "text-align": "left", "margin": "0px",
                                                       "--hover-color": "#eee"},
                                          "nav-link-selected": {"background-color": "green"},
                                      }
                                      )

    if selected_horizontal == 'Restart':
        select_folder_streamlit()
        st.warning('Press F5 or refresh the web page', icon='⚠')

    if selected_horizontal == 'Home':
        select_folder_project()

    # charger fichier *.node
    if selected_horizontal == 'Load':
        # select_folder_project()
        loaded_file = st.file_uploader("Choose a file", type='node')
        if loaded_file:
            st.session_state['file_node'] = loaded_file.name
            # st.write('file : ', st.session_state['file_node'])
            st.session_state['code'] = loaded_file.getvalue().decode('utf-8')
            view_code_node()
            st.session_state['loaded'] = True
        st.stop()

    if selected_horizontal == 'Save':
        select_folder_project()
        file_save = st.session_state['file_node']
        # st.write('file : ', st.session_state['file_node'])
        file_code = st.session_state['code']
        # st.write(st.session_state['code'])
        # st.write(file_save)
        with open(file_save, "w") as f:
            f.write(file_code)  # save code init file
            st.info(f'save {file_save}')
            view_code_node()
            st.session_state['loaded'] = False
            st.stop()

    if selected_horizontal == 'New':
        if is_file_exist(node):  # node existant ?
            st.warning(f" node {node} exist , please select Load node")
            time.sleep(0.1)

        else:
            st.session_state['code'] = f"node {node}\n"
            # code_editeur = view_code_node()
            code_editeur = st_ace(value=f"node {node}\n", language='forth', theme='cobalt', font_size=25,
                                  auto_update=False,
                                  key='new')
            node_file = f"{code_editeur.title().split()[1]}.node"  # ['Node','117']  '117.node'
            folder_file = f"{st.session_state['folder_project']}/{node_file}".strip()
            st.text(f"Node : {folder_file}")
            st.session_state['file_node'] = node_file
            st.session_state['code'] = code_editeur
            st.stop()  # attente save

    if selected_vertical_menu == 'About':
        st.info('informational message GA144 program ', icon="ℹ️")

    # gestion port serie
    if selected_vertical_menu == 'Setting-communication':
        message = ''
        ports = serial.tools.list_ports.comports()
        list_port = []
        for port, desc, hwid in sorted(ports):
            list_port.append(port)
        option_port_serial = st.selectbox('Serial Port selection', list_port)
        st.session_state['serial_port'] = option_port_serial
        time.sleep(0.1)
        st.write('You selected:', st.session_state['serial_port'])

    # gestion GA144 nodes
    my_expander = st.expander(label=f"GA144 Nodes {str(file_in_folder()).replace('.node', '').replace('init', '')} ")

    with my_expander:
        list_node_button = [

            "700", "701", "702", "703", "704", "705", "706", "707", "708", "709", "710", "711", "712", "713", "714",
            "715",
            "716", "717",
            "600", "601", "602", "603", "604", "605", "606", "607", "608", "609", "610", "611", "612", "613", "614",
            "615",
            "616", "617",
            "500", "501", "502", "503", "504", "505", "506", "507", "508", "509", "510", "511", "512", "513", "514",
            "515",
            "516", "517",
            "400", "401", "402", "403", "404", "405", "406", "407", "408", "409", "410", "411", "412", "413", "414",
            "415",
            "416", "417",
            "300", "301", "302", "303", "304", "305", "306", "307", "308", "309", "310", "311", "312", "313", "314",
            "315",
            "316", "317",
            "200", "201", "202", "203", "204", "205", "206", "207", "208", "209", "210", "211", "212", "213", "214",
            "215",
            "216", "217",
            "100", "101", "102", "103", "104", "105", "106", "107", "108", "109", "110", "111", "112", "113", "114",
            "115",
            "116", "117",
            "000", "001", "002", "003", "004", "005", "006", "007", "008", "009", "010", "011", "012", "013", "014",
            "015",
            "016", "017"
        ]

        cols = cycle(st.columns(18))  # st.columns here since it is out of beta at the time I'm writing this
        for idx, button_node in enumerate(list_node_button):
            if button_node in str(file_in_folder()):  # find nodes
                type_ = 'primary'
                help_ = find_fonction_node(button_node)
            else:
                type_ = 'secondary'
                help_ = ''
            next(cols).button(label=str(button_node), type=type_, help=help_)

    expander_compilation = st.expander(label=f"GA144 compilation  ")
    container_compilation = st.container()

    with expander_compilation:
        if st.session_state['compilation_file']:
            # container_compilation.write("GA144 compilation  ")
            stdout, stderr = st.columns(2)
            with redirect_stdout(io.StringIO()) as stdout_f, redirect_stderr(io.StringIO()) as stderr_f:
                try:
                    select_folder_streamlit()
                    # ga144compilation_process = subprocess.run(["pwd"], capture_output=True, text=True)
                    # ga144compilation_process = subprocess.run(["python", "ga.py",f"{st.session_state['name_projet']}/{st.session_state['name_projet']}.Cga_"],capture_output=True, text=True)
                    p = Path(f"{st.session_state['folder_project']}/{st.session_state['name_projet']}.Cga_")
                    st.write(p)
                    ga144size_compilation_process = subprocess.run(["python", "ga.py", p, "--size"],
                                                                   capture_output=True, check=True, text=True)
                    ga144compilation_process = subprocess.run(["python", "ga.py", p],
                                                              capture_output=True, text=True)
                    stdout_f.write(ga144size_compilation_process.stdout)  # --size   Count node ram usage
                    stdout_f.write(ga144compilation_process.stdout)
                    stderr_f.write(ga144compilation_process.stderr)

                    # print(read_file(st.session_state['compilation_file']))
                    print(read_file(f"{st.session_state['folder_project']}/{st.session_state['compilation_file']}_"))

                except Exception as e:
                    traceback.print_exc()
                    traceback.print_exc(file=sys.stdout)  # or sys.stdout
            stdout_text = stdout_f.getvalue()
            stdout.text(stdout_text)
            stderr_text = stderr_f.getvalue()
            stderr.text(stderr_text)

    expander_send = st.expander(label=f"GA144 send  ")

    with expander_send:
        if st.session_state['send']:
            stdout, stderr = st.columns(2)
            with redirect_stdout(io.StringIO()) as stdout_f, redirect_stderr(io.StringIO()) as stderr_f:
                try:
                    select_folder_streamlit()
                    # ga144send_process = subprocess.run(["pwd"], capture_output=True, text=True)
                    # ga144send_process = subprocess.run(["python", "ga.py", f"{st.session_state['name_projet']}/{st.session_state['name_projet']}.Cga_","--port", f"{st.session_state['serial_port']}"], capture_output=True, text=True)
                    p = Path(f"{st.session_state['folder_project']}/{st.session_state['name_projet']}.Cga_")
                    st.write(f"Send to {st.session_state['serial_port']}")
                    # ga144send_process = subprocess.run(["python", "ga.py", p,"--port", f"{st.session_state['serial_port']}"], capture_output=True, timeout=5, check=True,text=True)
                    ga144send_process = subprocess.Popen(
                        ["python", "ga.py", p, "--port", f"{st.session_state['serial_port']}"], stdout=subprocess.PIPE)

                    st.text(ga144send_process.stdout.read().decode())
                    # ga144send_process.wait(timeout=5)
                    if st.button("End"):
                        ga144send_process.kill()
                except Exception as e:
                    traceback.print_exc()
                    traceback.print_exc(file=sys.stdout)  # or sys.stdout
            st.session_state['send'] = False

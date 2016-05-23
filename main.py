# -*- coding: utf-8 -*-
import tornado.ioloop
import tornado.web
import os
import requests
import json
            
# echo team as list to store them
# [team1_prjs, team2_prjs]
projects_list = []

# [prj1_tasks, prj2_tasks]
tasks_list = []
# [prj1_groups, prj2_groups]
groups_list = []

headers = {"Content-Type": "application/json"}
session = None
def init_session():
    global session
    session = requests.Session()

def get_userinfo(session):
    global headers
    url = "https://api.worktile.com/v1/user/profile"
    r = session.get(url, headers=headers)
    data = json.loads(r.content)
    print "UserName: ", data['display_name']

def get_team(session):
    global headers
    team_ids = [] 
    url = "https://api.worktile.com/v1/teams"
    r = session.get(url, headers=headers)
    data = json.loads(r.content)
    for team in data:
        print "TeamID: ", team['team_id']
        print "TeamName: ", team['name']
        team_ids.append(team['team_id'])
    return team_ids

def get_projects(session, team_id):
    global headers
    
    projects_list = []
    url = "https://api.worktile.com/v1/teams/" + team_id + "/projects"
    r = session.get(url, headers=headers)
    data = json.loads(r.content)
    for project in data:
        #print "ProjectID: ", project['pid']
        #print "ProjectName: ", project['name']
        projects_list.append(dict(id=project['pid'], name=project['name']))

    print projects_list
    return projects_list

def get_task_group(session, pid):
    global headers
    groups_list = []
    url = "https://api.worktile.com/v1/entries?pid=" + pid
    r = session.get(url, headers=headers)
    data = json.loads(r.content)
    for grp in data:
        groups_list.append(dict(pid=pid, gid=grp['entry_id'], name=grp['name'])) 

    #print groups_list
    return groups_list

def get_tasklist(session, pid):
    global headers
    tasks_list = []
    url = "https://api.worktile.com/v1/tasks?pid=" + pid
    r = session.get(url, headers=headers)
    data = json.loads(r.content)
    for task in data:
        tasks_list.append(dict(name=task['name'],
            gid=task['entry_id'],
            tid=task['tid'],
            pid=task['pid']))
    #print tasks_list
    return tasks_list

def generate_data(projects, groups, tasks):
    # projects : pid, name
    # groups: pid, gid, name
    # tasks: gid, tid, pid, name
    for ps,gs,ts in projects, groups, tasks:
        for p,g,t in ps,gs,ts:
            pass

class MainHandler(tornado.web.RequestHandler):
    datas = {
            "client_id": "d696ca9c255f4a9a832bb1b127a41196",
            "client_secret": "665cfcc46fa243b1a6435f6cb77a709a",
            "code": ""
        }

    code = None
    def get(self):
        global headers, session
        self.code = self.get_arguments('code')
        if len(self.code):
            self.code = str(self.code[0])
            print self.code
            self.datas['code'] = str(self.code)
            r = session.post("https://api.worktile.com/oauth2/access_token", data=json.dumps(self.datas), headers=headers)
            data = json.loads(r.content)
            print data
            headers['access_token'] = data['access_token']
            get_userinfo(session)
            team_list = get_team(session)
            print team_list

            global projects_list, tasks_list, groups_list
            for tid in team_list:
                projects_list.append(get_projects(session, tid))
            print projects_list

            for team_p in projects_list:
                for p in team_p:
                    #print p
                    tasks_list.append(get_tasklist(session, p['id']))
                    groups_list.append(get_task_group(session, p['id']))

            self.redirect("/kernel")
        else:
            self.redirect("https://open.worktile.com/oauth2/authorize?client_id=d696ca9c255f4a9a832bb1b127a41196&redirect_uri=http://report.blackrose.me")
        

class GetReport(tornado.web.RequestHandler):
    global projects_list, tasks_list, groups_list
    def get(self):
        #data = generate_data(projects_list, groups_list, tasks_list)
        self.render("index.html", projects_list=projects_list,
                tasks_list=tasks_list, groups_list=groups_list)

class GenerateReport(tornado.web.RequestHandler):
    global projects_list, tasks_list, groups_list
    def post(self):
        print self.get_argument("project-ids")
        pid = "88be3a3cf4b64b0e8eb5f66f72be20aa"
        group_id = "2eca600c642145659164b871cfadfd3a"
        tasks = []
        prjs = []
        for prj in projects_list:
            for p in prj:
                if p['id'] == pid:
                    prjs.append(p)

        for tks in tasks_list:
            for t in tks:
                if t["pid"] == pid:
                    tasks.append(t)
        groups = []
        for g in tasks:
            if g['gid'] == group_id:
                groups.append(g['name'])
        print groups_list
        self.render("report.html", groups_list=groups,
                prjs_list = prjs, tasks_list = tasks)


if __name__ == "__main__":
    init_session()
    application = tornado.web.Application([
        ("/", MainHandler),
        ("/kernel", GetReport),
        ("/generate_report", GenerateReport),
        ],
        template_path = os.path.join(os.path.dirname(__file__), "templates"),
        static_path = os.path.join(os.path.dirname(__file__), "templates/static")
    )

    application.listen(8888)
    tornado.ioloop.IOLoop.current().start()

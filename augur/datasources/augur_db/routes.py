#SPDX-License-Identifier: MIT
"""
Creates routes for the Augur database data source plugin
"""

from flask import request, Response

def create_routes(server):

    augur_db = server._augur['augur_db']()

    """
    @api {get} /repo-groups Repo Groups
    @apiName repo-groups
    @apiGroup Utility
    @apiDescription Get all the downloaded repo groups.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_group_id": 20,
                            "rg_name": "Rails",
                            "rg_description": "Rails Ecosystem.",
                            "rg_website": "",
                            "rg_recache": 0,
                            "rg_last_modified": "2019-06-03T15:55:20.000Z",
                            "rg_type": "GitHub Organization",
                            "tool_source": "load",
                            "tool_version": "one",
                            "data_source": "git",
                            "data_collection_date": "2019-06-05T13:36:25.000Z"
                        },
                        {
                            "repo_group_id": 23,
                            "rg_name": "Netflix",
                            "rg_description": "Netflix Ecosystem.",
                            "rg_website": "",
                            "rg_recache": 0,
                            "rg_last_modified": "2019-06-03T15:55:20.000Z",
                            "rg_type": "GitHub Organization",
                            "tool_source": "load",
                            "tool_version": "one",
                            "data_source": "git",
                            "data_collection_date": "2019-06-05T13:36:36.000Z"
                        }
                    ]
    """
    @server.app.route('/{}/repo-groups'.format(server.api_version))
    def get_repo_groups(): #TODO: make this name automatic - wrapper?
        drs = server.transform(augur_db.repo_groups)
        return Response(response=drs,
                        status=200,
                        mimetype="application/json")
    server.updateMetricMetadata(function=augur_db.repo_groups, endpoint='/{}/repo-groups'.format(server.api_version), metric_type='git')

    """
    @api {get} /repos Repos
    @apiName repos
    @apiGroup Utility
    @apiDescription Get all the downloaded repos.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21996,
                            "repo_name": "incubator-argus",
                            "description": null,
                            "url": "github.com\/apache\/incubator-argus.git",
                            "repo_status": "Update",
                            "commits_all_time": null,
                            "issues_all_time": null,
                            "rg_name": "Apache",
                            "base64_url": "Z2l0aHViLmNvbS9hcGFjaGUvaW5jdWJhdG9yLWFyZ3VzLmdpdA=="
                        },
                        {
                            "repo_id": 21729,
                            "repo_name": "tomee-site",
                            "description": null,
                            "url": "github.com\/apache\/tomee-site.git",
                            "repo_status": "Complete",
                            "commits_all_time": 224216,
                            "issues_all_time": 2,
                            "rg_name": "Apache",
                            "base64_url": "Z2l0aHViLmNvbS9hcGFjaGUvdG9tZWUtc2l0ZS5naXQ="
                        }
                    ]
    """
    @server.app.route('/{}/repos'.format(server.api_version))
    def downloaded_repos():
        drs = server.transform(augur_db.downloaded_repos)
        return Response(response=drs,
                        status=200,
                        mimetype="application/json")

    server.updateMetricMetadata(function=augur_db.downloaded_repos, endpoint='/{}/repos'.format(server.api_version), metric_type='git')

    """
    @api {get} /repo-groups/:repo_group_id/repos Repos in Repo Group
    @apiName repos-in-repo-groups
    @apiGroup Utility
    @apiDescription Get all the repos in a repo group.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21326,
                            "repo_name": "graphql-js",
                            "description": null,
                            "url": "https:\/\/github.com\/graphql\/graphql-js.git",
                            "repo_status": "Complete",
                            "commits_all_time": 6874,
                            "issues_all_time": 81
                        },
                        {
                            "repo_id": 21331,
                            "repo_name": "graphiql",
                            "description": null,
                            "url": "https:\/\/github.com\/graphql\/graphiql.git",
                            "repo_status": "Complete",
                            "commits_all_time": 4772,
                            "issues_all_time": 144
                        }
                    ]
    """
    server.addRepoGroupMetric(augur_db.repos_in_repo_groups, 'repos')

    """
    @api {get} /repos/:owner/:repo Get Repo
    @apiName get-repo
    @apiGroup Utility
    @apiDescription Get the `repo_group_id` & `repo_id` of a particular repo.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21339,
                            "repo_group_id": 23
                        },
                        {
                            "repo_id": 21000,
                            "repo_group_id": 20
                        }
                    ]
    """
    @server.app.route('/{}/repos/<owner>/<repo>'.format(server.api_version))
    def get_repo(owner, repo):
        a = [owner, repo]
        gre = server.transform(augur_db.get_repo, args = a)
        return Response(response=gre,
                        status=200,
                        mimetype="application/json")

    server.updateMetricMetadata(function=augur_db.get_repo, endpoint='/{}/repos/<owner>/<repo>'.format(server.api_version), metric_type='git')

    @server.app.route('/{}/dosocs/repos'.format(server.api_version))
    def get_repos_for_dosocs():
        res = server.transform(augur_db.get_repos_for_dosocs)
        return Response(response=res,
                        status=200,
                        mimetype='application/json')

    server.addRepoGroupMetric(augur_db.get_issues, 'get-issues')
    server.addRepoMetric(augur_db.get_issues, 'get-issues')
    #####################################
    ###           EVOLUTION           ###
    #####################################

    """
    @api {get} /repo-groups/:repo_group_id/code-changes Code Changes (Repo Group)
    @apiName code-changes-repo-group
    @apiGroup Evolution
    @apiDescription Time series of number of commits during a certain period.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/Code_Changes.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiParam {string=day, week, month, year} [period="day"] Periodicity specification.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21337,
                            "repo_name": "graphql-wg",
                            "date": "2018-01-01T00:00:00.000Z",
                            "commit_count": 173
                        },
                        {
                            "repo_id": 21337,
                            "repo_name": "graphql-wg",
                            "date": "2019-01-01T00:00:00.000Z",
                            "commit_count": 92
                        },
                        {
                            "repo_id": 21338,
                            "repo_name": "foundation",
                            "date": "2019-01-01T00:00:00.000Z",
                            "commit_count": 8
                        }
                    ]
    """
    server.addRepoGroupMetric(augur_db.code_changes, 'code-changes')

    """
    @api {get} /repo-groups/:repo_group_id/repos/:repo_id/code-changes Code Changes (Repo)
    @apiName code-changes-repo
    @apiGroup Evolution
    @apiDescription Time series number of commits during a certain period.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/Code_Changes.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiParam {string=day, week, month, year} [period="day"] Periodicity specification.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_name": "graphql",
                            "date": "2015-01-01T00:00:00.000Z",
                            "commit_count": 90,
                        },
                        {
                            "repo_name": "graphql",
                            "date": "2016-01-01T00:00:00.000Z",
                            "commit_count": 955,
                        }
                    ]
    """
    server.addRepoMetric(augur_db.code_changes, 'code-changes')

    """
    @api {get} /repo-groups/:repo_group_id/code-changes-lines Code Changes Lines (Repo Group)
    @apiName code-changes-lines-repo-group
    @apiGroup Evolution
    @apiDescription Time series of lines added & removed during a certain period.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/Code_Changes_Lines.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiParam {string=day, week, month, year} [period="day"] Periodicity specification.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21337,
                            "repo_name": "graphql-wg",
                            "date": "2018-01-01T00:00:00.000Z",
                            "added": 1135,
                            "removed": 101
                        },
                        {
                            "repo_id": 21337,
                            "repo_name": "graphql-wg",
                            "date": "2019-01-01T00:00:00.000Z",
                            "added": 872,
                            "removed": 76
                        },
                        {
                            "repo_id": 21338,
                            "repo_name": "foundation",
                            "date": "2019-01-01T00:00:00.000Z",
                            "added": 130,
                            "removed": 5
                        }
                    ]
    """
    server.addRepoGroupMetric(augur_db.code_changes_lines, 'code-changes-lines')

    """
    @api {get} /repo-groups/:repo_group_id/repos/:repo_id/code-changes-lines Code Changes Lines (Repo)
    @apiName code-changes-lines-repo
    @apiGroup Evolution
    @apiDescription Time series of lines added & removed during a certain period.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/Code_Changes_Lines.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiParam {string=day, week, month, year} [period="day"] Periodicity specification.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_name": "graphql-js",
                            "date": "2015-06-01T00:00:00.000Z",
                            "added": 17613,
                            "removed": 106
                        },
                        {
                            "repo_name": "graphql-js",
                            "date": "2015-07-01T00:00:00.000Z",
                            "added": 9448,
                            "removed": 5081
                        },
                        {
                            "repo_name": "graphql-js",
                            "date": "2015-08-01T00:00:00.000Z",
                            "added": 6270,
                            "removed": 3833
                        }
                    ]
    """
    server.addRepoMetric(augur_db.code_changes_lines, 'code-changes-lines')

    """
    @api {get} /repo-groups/:repo_group_id/issues-new Issues New (Repo Group)
    @apiName issues-new-repo-group
    @apiGroup Evolution
    @apiDescription Time series of number of new issues opened during a certain period.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/Issues_New.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiParam {string=day, week, month, year} [period="day"] Periodicity specification.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21000,
                            "repo_name": "rails",
                            "date": "2019-01-01T00:00:00.000Z",
                            "issues": 318
                        },
                        {
                            "repo_id": 21002,
                            "repo_name": "acts_as_list",
                            "date": "2009-01-01T00:00:00.000Z",
                            "issues": 1
                        },
                        {
                            "repo_id": 21002,
                            "repo_name": "acts_as_list",
                            "date": "2010-01-01T00:00:00.000Z",
                            "issues": 7
                        }
                    ]
    """
    server.addRepoGroupMetric(augur_db.issues_new, 'issues-new')

    """
    @api {get} /repo-groups/:repo_group_id/repos/:repo_id/issues-new Issues New (Repo)
    @apiName issues-new-repo
    @apiGroup Evolution
    @apiDescription Time series of number of new issues opened during a certain period.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/Issues_New.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiParam {string=day, week, month, year} [period="day"] Periodicity specification.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_name": "rails",
                            "date": "2015-01-01T00:00:00.000Z",
                            "issues": 116
                        },
                        {
                            "repo_name": "rails",
                            "date": "2016-01-01T00:00:00.000Z",
                            "issues": 196
                        },
                        {
                            "repo_name": "rails",
                            "date": "2017-01-01T00:00:00.000Z",
                            "issues": 180
                        }
                    ]
    """
    server.addRepoMetric(augur_db.issues_new, 'issues-new')

    """
    @api {get} /repo-groups/:repo_group_id/issues-active Issues Active (Repo Group)
    @apiName issues-active-repo-group
    @apiGroup Evolution
    @apiDescription Time series of number of issues that showed some activity during a certain period.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/Issues_Active.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiParam {string=day, week, month, year} [period="day"] Periodicity specification.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21039,
                            "repo_name": "rails_xss",
                            "date": "2019-01-01T00:00:00.000Z",
                            "issues": 18
                        },
                        {
                            "repo_id": 21041,
                            "repo_name": "prototype-rails",
                            "date": "2019-01-01T00:00:00.000Z",
                            "issues": 20
                        },
                        {
                            "repo_id": 21043,
                            "repo_name": "sprockets-rails",
                            "date": "2015-01-01T00:00:00.000Z",
                            "issues": 102
                        }
                    ]
    """
    server.addRepoGroupMetric(augur_db.issues_active, 'issues-active')

    """
    @api {get} /repo-groups/:repo_group_id/repos/:repo_id/issues-active Issues Active (Repo)
    @apiName issues-active-repo
    @apiGroup Evolution
    @apiDescription Time series of number of issues that showed some activity during a certain period.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/Issues_Active.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiParam {string=day, week, month, year} [period="day"] Periodicity specification.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_name": "rails",
                            "date": "2011-01-01T00:00:00.000Z",
                            "issues": 30
                        },
                        {
                            "repo_name": "rails",
                            "date": "2012-01-01T00:00:00.000Z",
                            "issues": 116
                        },
                        {
                            "repo_name": "rails",
                            "date": "2013-01-01T00:00:00.000Z",
                            "issues": 479
                        }
                    ]
    """
    server.addRepoMetric(augur_db.issues_active, 'issues-active')

    """
    @api {get} /repo-groups/:repo_group_id/issues-closed Issues Closed (Repo Group)
    @apiName issues-closed-repo-group
    @apiGroup Evolution
    @apiDescription Time series of number of issues closed during a certain period.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/Issues_Closed.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiParam {string=day, week, month, year} [period="day"] Periodicity specification.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21681,
                            "repo_name": "incubator-zipkin",
                            "date": "2019-01-01T00:00:00.000Z",
                            "issues": 425
                        },
                        {
                            "repo_id": 21682,
                            "repo_name": "incubator-dubbo",
                            "date": "2013-01-01T00:00:00.000Z",
                            "issues": 7
                        },
                        {
                            "repo_id": 21682,
                            "repo_name": "incubator-dubbo",
                            "date": "2014-01-01T00:00:00.000Z",
                            "issues": 47
                        }
                    ]
    """
    server.addRepoGroupMetric(augur_db.issues_closed, 'issues-closed')

    """
    @api {get} /repo-groups/:repo_group_id/repos/:repo_id/issues-closed Issues Closed (Repo)
    @apiName issues-closed-repo
    @apiGroup Evolution
    @apiDescription Time series of number of issues closed during a certain period.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/Issues_New.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiParam {string=day, week, month, year} [period="day"] Periodicity specification.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_name": "incubator-pagespeed-ngx",
                            "date": "2012-01-01T00:00:00.000Z",
                            "issues": 97
                        },
                        {
                            "repo_name": "incubator-pagespeed-ngx",
                            "date": "2013-01-01T00:00:00.000Z",
                            "issues": 395
                        },
                        {
                            "repo_name": "incubator-pagespeed-ngx",
                            "date": "2014-01-01T00:00:00.000Z",
                            "issues": 265
                        }
                    ]
    """
    server.addRepoMetric(augur_db.issues_closed, 'issues-closed')

    """
    @api {get} /repo-groups/:repo_group_id/issue-duration Issue Duration (Repo Group)
    @apiName issue-duration-repo-group
    @apiGroup Evolution
    @apiDescription Time since an issue is proposed until it is closed.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/focus_areas/code_development.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21017,
                            "repo_name": "ssl_requirement",
                            "issue_id": 50320,
                            "created_at": "2011-05-06T20:20:05.000Z",
                            "closed_at": "2011-05-06T20:21:47.000Z",
                            "duration": "0 days 00:01:42.000000000"
                        },
                        {
                            "repo_id": 21027,
                            "repo_name": "rails-contributors",
                            "issue_id": 50328,
                            "created_at": "2019-06-20T22:56:38.000Z",
                            "closed_at": "2019-06-21T20:17:28.000Z",
                            "duration": "0 days 21:20:50.000000000"
                        },
                        {
                            "repo_id": 21027,
                            "repo_name": "rails-contributors",
                            "issue_id": 50329,
                            "created_at": "2019-06-20T22:01:52.000Z",
                            "closed_at": "2019-06-22T02:29:03.000Z",
                            "duration": "1 days 04:27:11.000000000"
                        }
                    ]
    """
    server.addRepoGroupMetric(augur_db.issue_duration, 'issue-duration')

    """
    @api {get} /repo-groups/:repo_group_id/repos/:repo_id/issue-backlog Issue Duration (Repo)
    @apiName issue-duration-repo
    @apiGroup Evolution
    @apiDescription Time since an issue is proposed until it is closed.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/focus_areas/code_development.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_name": "exception_notification",
                            "issue_id": 50306,
                            "created_at": "2011-02-13T03:46:06.000Z",
                            "closed_at": "2011-04-14T23:27:33.000Z",
                            "duration": "60 days 19:41:27.000000000"
                        },
                        {
                            "repo_name": "exception_notification",
                            "issue_id": 50308,
                            "created_at": "2011-01-19T18:47:41.000Z",
                            "closed_at": "2013-12-09T13:51:03.000Z",
                            "duration": "1054 days 19:03:22.000000000"
                        }
                    ]
    """
    server.addRepoMetric(augur_db.issue_duration, 'issue-duration')

    """
    @api {get} /repo-groups/:repo_group_id/issue-participants Issue Participants (Repo Group)
    @apiName issue-participants-repo-group
    @apiGroup Evolution
    @apiDescription How many persons participated in the discussion of issues.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/focus_areas/code_development.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21027,
                            "repo_name": "rails-contributors",
                            "issue_id": 50328,
                            "created_at": "2019-06-20T22:56:38.000Z",
                            "participants": 1
                        },
                        {
                            "repo_id": 21030,
                            "repo_name": "arel",
                            "issue_id": 50796,
                            "created_at": "2017-03-02T21:14:46.000Z",
                            "participants": 1
                        },
                        {
                            "repo_id": 21030,
                            "repo_name": "arel",
                            "issue_id": 50795,
                            "created_at": "2017-03-24T15:39:08.000Z",
                            "participants": 2
                        }
                    ]
    """
    server.addRepoGroupMetric(augur_db.issue_participants, 'issue-participants')

    """
    @api {get} /repo-groups/:repo_group_id/repos/:repo_id/issue-participants Issue Participants (Repo)
    @apiName issue-participants-repo
    @apiGroup Evolution
    @apiDescription How many persons participated in the discussion of issues.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/focus_areas/code_development.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_name": "arel",
                            "issue_id": 50796,
                            "created_at": "2017-03-02T21:14:46.000Z",
                            "participants": 1
                        },
                        {
                            "repo_name": "arel",
                            "issue_id": 50795,
                            "created_at": "2017-03-24T15:39:08.000Z",
                            "participants": 2
                        }
                    ]
    """
    server.addRepoMetric(augur_db.issue_participants, 'issue-participants')

    """
    @api {get} /repo-groups/:repo_group_id/issue-backlog Issue Backlog (Repo Group)
    @apiName issue-backlog-repo-group
    @apiGroup Evolution
    @apiDescription Number of issues currently open.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/focus_areas/code_development.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21055,
                            "repo_name": "cache_digests",
                            "issue_backlog": 21
                        },
                        {
                            "repo_id": 21056,
                            "repo_name": "rails-dev-box",
                            "issue_backlog": 1
                        },
                        {
                            "repo_id": 21058,
                            "repo_name": "activerecord-session_store",
                            "issue_backlog": 24
                        }
                    ]
    """
    server.addRepoGroupMetric(augur_db.issue_backlog, 'issue-backlog')

    """
    @api {get} /repo-groups/:repo_group_id/repos/:repo_id/issue-backlog Issue Backlog (Repo)
    @apiName issue-backlog-repo
    @apiGroup Evolution
    @apiDescription Number of issues currently open.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/focus_areas/code_development.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_name":"render_component",
                            "issue_backlog": 3
                        }
                    ]
    """
    server.addRepoMetric(augur_db.issue_backlog, 'issue-backlog')

    """
    @api {get} /repo-groups/:repo_group_id/issue-throughput Issue Throughput (Repo Group)
    @apiName issue-throughput-repo-group
    @apiGroup Evolution
    @apiDescription Ratio of issues closed to total issues.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/focus_areas/code_development.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21681,
                            "repo_name": "incubator-zipkin",
                            "throughput": 0.819125
                        },
                        {
                            "repo_id": 21682,
                            "repo_name": "incubator-dubbo",
                            "throughput": 0.861896
                        }
                    ]
    """
    server.addRepoGroupMetric(augur_db.issue_throughput, 'issue-throughput')

    """
    @api {get} /repo-groups/:repo_group_id/repos/:repo_id/issue-throughput Issue Throughput (Repo)
    @apiName issue-throughput-repo
    @apiGroup Evolution
    @apiDescription Ratio of issues closed to total issues.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/focus_areas/code_development.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_name": "rails-contributors",
                            "throughput": 0.997531
                        }
                    ]
    """
    server.addRepoMetric(augur_db.issue_throughput, 'issue-throughput')

    # @server.app.route('/{}/repo-groups/<repo_group_id>/code-changes'.format(server.api_version))
    # def code_changes_repo_group_route(repo_group_id):
    #     period = request.args.get('period', 'day')
    #     begin_date = request.args.get('begin_date')
    #     end_date = request.args.get('end_date')

    #     kwargs = {'repo_group_id': repo_group_id, 'period': period,
    #               'begin_date': begin_date, 'end_date': end_date}

    #     data = server.transform(augur_db.code_changes,
    #                             args=[],
    #                             kwargs=kwargs)

    #     return Response(response=data, status=200, mimetype='application/json')

    # @server.app.route('/{}/repo-groups/<repo_group_id>/repo/<repo_id>/code-changes'.format(server.api_version))
    # def code_changes_repo_route(repo_group_id, repo_id):
    #     period = request.args.get('period', 'day')
    #     begin_date = request.args.get('begin_date')
    #     end_date = request.args.get('end_date')

    #     kwargs = {'repo_group_id': repo_group_id, 'repo_id': repo_id,
    #               'period': period, 'begin_date': begin_date,
    #               'end_date': end_date}

    #     data = server.transform(augur_db.code_changes,
    #                             args=[],
    #                             kwargs=kwargs)

    #     return Response(response=data, status=200, mimetype='application/json')

    """
    @api {get} /repo-groups/:repo_group_id/pull-requests-merge-contributor-new New Contributors of Commits (Repo Group)
    @apiName New Contributors of Commits(Repo Group)
    @apiGroup Evolution
    @apiDescription Number of persons contributing with an accepted commit for the first time.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/pull-requests-merge-contributor-new.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiParam {string=day, week, month, year} [period="day"] Periodicity specification.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "commit_date": "2018-01-01T00:00:00.000Z",
                            "count": 5140,
                            "repo_name": "rails"
                        },
                        {
                            "commit_date": "2019-01-01T00:00:00.000Z",
                            "commit_count": 711,
                            "repo_name": "rails"
                        }
                    ]
    """
    server.addRepoGroupMetric(
        augur_db.pull_requests_merge_contributor_new, 'pull-requests-merge-contributor-new')

    """
    @api {get} /repo-groups/:repo_group_id/repos/:repo_id/pull-requests-merge-contributor-new New Contributors of Commits (Repo)
    @apiName New Contributors of Commits(Repo)
    @apiGroup Evolution
    @apiDescription Number of persons contributing with an accepted commit for the first time.
                <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/pull-requests-merge-contributor-new.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiParam {string=day, week, month, year} [period="day"] Periodicity specification.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "commit_date": "2018-01-01T00:00:00.000Z",
                            "count": 2287,
                            "repo_name": "rails"
                        },
                        {
                            "commit_date": "2018-02-01T00:00:00.000Z",
                            "count": 1939,
                            "repo_name": "rails"
                        }
                    ]
    """
    server.addRepoMetric(
        augur_db.pull_requests_merge_contributor_new, 'pull-requests-merge-contributor-new')

    """
    @api {get} /repo-groups/:repo_group_id/issues-first-time-opened New Contributors of Issues (Repo Group)
    @apiName New Contributors of Issues(Repo Group)
    @apiGroup Evolution
    @apiDescription Number of persons opening an issue for the first time.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/issues-first-time-opened.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiParam {string=day, week, month, year} [period="day"] Periodicity specification.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "issue_date": "2018-05-20T00:00:00.000Z",
                            "count": 3,
                            "repo_name": "rails",
                            "repo_id": 21000
                        },
                        {
                            "issue_date": "2019-06-03T00:00:00.000Z",
                            "count": 23,
                            "repo_name": "rails",
                            "repo_id": 21000
                        }
                    ]
    """
    server.addRepoGroupMetric(
        augur_db.issues_first_time_opened, 'issues-first-time-opened')

    """
    @api {get} /repo-groups/:repo_group_id/repos/:repo_id/issues-first-time-opened New Contributors of Issues (Repo)
    @apiName New Contributors of Issues(Repo)
    @apiGroup Evolution
    @apiDescription Number of persons opening an issue for the first time.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/issues-first-time-opened.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiParam {string=day, week, month, year} [period="day"] Periodicity specification.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "issue_date": "2018-05-20T00:00:00.000Z",
                            "count": 3,
                            "repo_name": "rails"
                        },
                        {
                            "issue_date": "2019-06-03T00:00:00.000Z",
                            "count": 23,
                            "repo_name": "rails"
                        }
                    ]
    """
    server.addRepoMetric(
        augur_db.issues_first_time_opened, 'issues-first-time-opened')

    """
    @api {get} /repo-groups/:repo_group_id/issues-first-time-closed Closed Issues New Contributor (Repo Group)
    @apiName Closed Issues New Contributors(Repo Group)
    @apiGroup Evolution
    @apiDescription Number of persons closing an issue for the first time.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/issues-first-time-closed.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiParam {string=day, week, month, year} [period="day"] Periodicity specification.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "issue_date": "2018-05-20T00:00:00.000Z",
                            "count": 3,
                            "repo_name": "rails",
                            "repo_id": 21000
                        },
                        {
                            "issue_date": "2019-06-03T00:00:00.000Z",
                            "count": 23
                            "repo_name": "rails",
                            "repo_id": 21000
                        }
                    ]
    """
    server.addRepoGroupMetric(
        augur_db.issues_first_time_closed, 'issues-first-time-closed')

    """
    @api {get} /repo-groups/:repo_group_id/repos/:repo_id/issues-first-time-closed Closed Issues New Contributors (Repo)
    @apiName Closed Issues New Contributors(Repo)
    @apiGroup Evolution
    @apiDescription Number of persons closing an issue for the first time.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/issues-first-time-closed.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiParam {string=day, week, month, year} [period="day"] Periodicity specification.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "issue_date": "2018-05-20T00:00:00.000Z",
                            "count": 3,
                            "repo_name": "rails"
                        },
                        {
                            "issue_date": "2019-06-03T00:00:00.000Z",
                            "count": 23,
                            "repo_name": "rails"
                        }
                    ]
    """
    server.addRepoMetric(
        augur_db.issues_first_time_closed, 'issues-first-time-closed')

    """
    @api {get} /repo-groups/:repo_group_id/sub-projects Sub-Projects (Repo Group)
    @apiName Sub-Projects(Repo Group)
    @apiGroup Evolution
    @apiDescription Number of sub-projects.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/sub-projects.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "sub_protject_count": 2
                        }
                    ]
    """
    server.addRepoGroupMetric(
        augur_db.sub_projects, 'sub-projects')

    """
    @api {get} /repo-groups/:repo_group_id/repos/:repo_id/sub-projects Sub-Projects (Repo)
    @apiName Sub-Projects(Repo)
    @apiGroup Evolution
    @apiDescription Number of sub-projects.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/sub-projects.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "sub_protject_count": 2
                        }
                    ]
    """
    server.addRepoMetric(
        augur_db.sub_projects, 'sub-projects')

    """
    @api {get} /repo-groups/:repo_group_id/contributors Contributors (Repo Group)
    @apiName Contributors(Repo Group)
    @apiGroup Evolution
    @apiDescription List of contributors and their contributions.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/contributors.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "user_id": 1,
                            "commits": 0,
                            "issues": 2,
                            "commit_comments": 0,
                            "issue_comments": 0,
                            "pull_requests": 0,
                            "pull_request_comments": 0,
                            "total": 2,
                            "repo_name": "rails",
                            "repo_id": 21000
                        },
                        {
                            "user_id": 2,
                            "commits": 0,
                            "issues": 2,
                            "commit_comments": 0,
                            "issue_comments": 0,
                            "pull_requests": 0,
                            "pull_request_comments": 0,
                            "total": 2,
                            "repo_name": "rails",
                            "repo_id": 21000
                        }
                    ]
    """
    server.addRepoGroupMetric(
        augur_db.contributors, 'contributors')

    """
    @api {get} /repo-groups/:repo_group_id/repos/:repo_id/contributors Contributors (Repo)
    @apiName Contributors(Repo)
    @apiGroup Evolution
    @apiDescription List of contributors and their contributions.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/contributors.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                       {
                            "user": 1,
                            "commits": 0,
                            "issues": 2,
                            "commit_comments": 0,
                            "issue_comments": 0,
                            "pull_requests": 0,
                            "pull_request_comments": 0,
                            "total": 2
                        },
                        {
                            "user": 2,
                            "commits": 0,
                            "issues": 2,
                            "commit_comments": 0,
                            "issue_comments": 0,
                            "pull_requests": 0,
                            "pull_request_comments": 0,
                            "total": 2
                        }
                    ]
    """
    server.addRepoMetric(
        augur_db.contributors, 'contributors')

    """
    @api {get} /repo-groups/:repo_group_id/contributors-new New Contributors (Repo Group)
    @apiName New Contributors(Repo Group)
    @apiGroup Evolution
    @apiDescription Time series of number of new contributors during a certain period.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/contributors-new.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiParam {string=day, week, month, year} [period="day"] Periodicity specification.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "contribute_at": "2018-05-20T00:00:00.000Z",
                            "count": 3,
                            "repo_name": "rails",
                            "repo_id": 21000
                        },
                        {
                            "contribute_at": "2019-06-03T00:00:00.000Z",
                            "count": 23,
                            "repo_name": "rails",
                            "repo_id": 21000
                        }
                    ]
    """
    server.addRepoGroupMetric(
        augur_db.contributors_new, 'contributors-new')

    """
    @api {get} /repo-groups/:repo_group_id/repos/:repo_id/contributors-new New Contributors (Repo)
    @apiName New Contributors(Repo)
    @apiGroup Evolution
    @apiDescription Time series of number of new contributors during a certain period.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/contributors-new.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiParam {string=day, week, month, year} [period="day"] Periodicity specification.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "contribute_at": "2018-05-20T00:00:00.000Z",
                            "count": 3,
                            "repo_name": "rails",
                            "repo_id": 21000
                        },
                        {
                            "contribute_at": "2019-06-03T00:00:00.000Z",
                            "count": 23,
                            "repo_name": "rails",
                            "repo_id": 21000
                        }
                    ]
    """
    server.addRepoMetric(
        augur_db.contributors_new, 'contributors-new')

    """
    @api {get} /repo-groups/:repo_group_id/open-issues-count Open Issues Count (Repo Group)
    @apiName open-issues-count-repo-group
    @apiGroup Evolution
    @apiDescription Count of open issues.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/contributors-new.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "rg_name": "Netflix",
                            "open_count": 1,
                            "date": "2017-09-11T00:00:00.000Z"
                        },
                        {
                            "rg_name": "Netflix",
                            "open_count": 4,
                            "date": "2019-06-10T00:00:00.000Z"
                        }
                    ]
    """
    server.addRepoGroupMetric(augur_db.open_issues_count, 'open-issues-count')

    """
    @api {get} /repo-groups/:repo_group_id/open-issues-count Open Issues Count (Repo)
    @apiName open-issues-count-repo
    @apiGroup Evolution
    @apiDescription Count of open issues.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/contributors-new.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiParam {string} repo_id Repository ID.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21681,
                            "open_count": 18,
                            "date": "2019-04-15T00:00:00.000Z"
                        },
                        {
                            "repo_id": 21681,
                            "open_count": 16,
                            "date": "2019-04-22T00:00:00.000Z"
                        }
                    ]
    """
    server.addRepoMetric(augur_db.open_issues_count, 'open-issues-count')

    """
    @api {get} /repo-groups/:repo_group_id/closed-issues-count Closed Issues Count (Repo Group)
    @apiName closed-issues-count-repo-group
    @apiGroup Evolution
    @apiDescription Count of closed issues.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/contributors-new.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "rg_name": "Apache",
                            "closed_count": 4,
                            "date": "2014-06-02T00:00:00.000Z"
                        },
                        {
                            "rg_name": "Apache",
                            "closed_count": 6,
                            "date": "2014-06-09T00:00:00.000Z"
                        }
                    ]
    """
    server.addRepoGroupMetric(augur_db.closed_issues_count, 'closed-issues-count')

    """
    @api {get} /repo-groups/:repo_group_id/closed-issues-count Closed Issues Count (Repo)
    @apiName closed-issues-count-repo
    @apiGroup Evolution
    @apiDescription Count of closed issues.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/contributors-new.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiParam {string} repo_id Repository ID.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21681,
                            "closed_count": 26,
                            "date": "2018-11-26T00:00:00.000Z"
                        },
                        {
                            "repo_id": 21681,
                            "closed_count": 14,
                            "date": "2018-12-03T00:00:00.000Z"
                        }
                    ]
    """
    server.addRepoMetric(augur_db.closed_issues_count, 'closed-issues-count')

    """
    @api {get} /repo-groups/:repo_group_id/issues-open-age Open Issue Age (Repo Group)
    @apiName Open Issue Age(Repo Group)
    @apiGroup Evolution
    @apiDescription Age of open issues.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/issues-open-age.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21000,
                            "repo_name": "rails",
                            "issue_id": 38318,
                            "date": "2009-05-15T19:48:43.000Z",
                            "open_date": 3696
                        },
                        {
                            "repo_id": 21000,
                            "repo_name": "rails",
                            "issue_id": 38317,
                            "date": "2009-05-16T14:35:40.000Z",
                            "open_date": 3695
                        }
                    ]
    """
    server.addRepoGroupMetric(
        augur_db.issues_open_age, 'issues-open-age')

    """
    @api {get} /repo-groups/:repo_group_id/repos/:repo_id/issues-open-age Open Issue Age (Repo)
    @apiName Open Issue Age(Repo)
    @apiGroup Evolution
    @apiDescription Age of open issues.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/issues-open-age.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21000,
                            "repo_name": "rails",
                            "issue_id": 38318,
                            "date": "2009-05-15T19:48:43.000Z",
                            "open_date": 3696
                        },
                        {
                            "repo_id": 21000,
                            "repo_name": "rails",
                            "issue_id": 38317,
                            "date": "2009-05-16T14:35:40.000Z",
                            "open_date": 3695
                        }
                    ]
    """
    server.addRepoMetric(
        augur_db.issues_open_age, 'issues-open-age')

    """
    @api {get} /repo-groups/:repo_group_id/issues-closed-resolution-duration Closed Issue Resolution Duration (Repo Group)
    @apiName Closed Issue Resolution Duration(Repo Group)
    @apiGroup Evolution
    @apiDescription Duration of time for issues to be resolved.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/issues-closed-resolution-duration.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiSuccessExample {json} Success-Response:
                   [
                        {
                            "repo_name":"incubator-dubbo",
                            "gh_issue_number":4110,
                            "issue_title":"rm incubating word",
                            "created_at":"2019-05-22T03:18:13.000Z",
                            "closed_at":"2019-05-22T05:27:29.000Z",
                            "diffdate":0.0
                        },
                        {
                            "repo_name":"incubator-dubbo",
                            "gh_issue_number":4111,
                            "issue_title":"nacos registry serviceName may conflict",
                            "created_at":"2019-05-22T03:30:23.000Z",
                            "closed_at":"2019-05-23T14:36:17.000Z",
                            "diffdate":1.0
                        }
                    ]
    """
    server.addRepoGroupMetric(
        augur_db.issues_closed_resolution_duration, 'issues-closed-resolution-duration')

    """
    @api {get} /repo-groups/:repo_group_id/repos/:repo_id/issues-closed-resolution-duration Closed Issue Resolution Duration (Repo)
    @apiName Closed Issue Resolution Duration(Repo)
    @apiGroup Evolution
    @apiDescription Duration of time for issues to be resolved.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/issues-closed-resolution-duration.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21682
                            "repo_name":"incubator-dubbo",
                            "gh_issue_number":4223,
                            "issue_title":"Cloud Native PR",
                            "created_at":"2019-05-31T07:55:44.000Z",
                            "closed_at":"2019-06-17T03:12:48.000Z",
                            "diffdate":16.0
                        },
                        {
                            "repo_id": 21682,
                             "repo_name":"incubator-dubbo",
                            "gh_issue_number":4131,
                            "issue_title":"Reduce context switching cost by optimizing thread model on consumer side.",
                            "created_at":"2019-05-23T06:18:21.000Z",
                            "closed_at":"2019-06-03T08:07:27.000Z",
                            "diffdate":11.0
                        }
                    ]
    """
    server.addRepoMetric(
        augur_db.issues_closed_resolution_duration, 'issues-closed-resolution-duration')

    """
    @api {get} /repo-groups/:repo_group_id/issues-maintainer-response-duration Issue Response Time (Repo Group)
    @apiName Issue Response Time(Repo Group)
    @apiGroup Evolution
    @apiDescription Duration of time for issues to be resolved.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/issues-maintainer-response-duration.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                   [
                        {
                            "repo_id": 21987,
                            "repo_name": "qpid-proton",
                            "average_days_comment": 27.1111111111
                        },
                        {
                            "repo_id": 22252,
                            "repo_name": "cordova-create",
                            "average_days_comment": 0.8
                        }
                    ]
    """
    server.addRepoGroupMetric(augur_db.issues_maintainer_response_duration, 'issues-maintainer-response-duration')

    """
    @api {get} /repo-groups/:repo_group_id/repos/:repo_id/issues-maintainer-response-duration Issue Response Time (Repo)
    @apiName Issue Response Time(Repo)
    @apiGroup Evolution
    @apiDescription Duration of time for issues to be resolved.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/issues-maintainer-response-duration.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiParam {string} repo_id Repository ID.
    @apiParam {string} [begin_date="1970-1-1 0:0:0"] Beginning date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiParam {string} [end_date="current date"] Ending date specification. E.g. values: `2018`, `2018-05`, `2019-05-01`
    @apiSuccessExample {json} Success-Response:
                   [
                        {
                            "repo_id": 21987,
                            "repo_name": "qpid-proton",
                            "average_days_comment": 27.1111111111
                        }
                    ]
    """
    server.addRepoMetric(augur_db.issues_maintainer_response_duration, 'issues-maintainer-response-duration')

    #####################################
    ###              RISK             ###
    #####################################

    """
    @api {get} /repo-groups/:repo_group_id/cii-best-practices-badge CII Best Practices Badge (Repo Group)
    @apiName cii-best-practices-badge-repo-group
    @apiGroup Risk
    @apiDescription The CII Best Practices Badge level.
                    <a href="https://github.com/chaoss/wg-risk/blob/master/focus-areas/security.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21252,
                            "repo_name": "php-legal-licenses",
                            "badge_level": "in_progress"
                        },
                        {
                            "repo_id": 21277,
                            "repo_name": "trickster",
                            "badge_level": "passing"
                        }
                    ]
    """
    server.addRepoGroupMetric(augur_db.cii_best_practices_badge, 'cii-best-practices-badge')

    """
    @api {get} /repo-groups/:repo_group_id/cii-best-practices-badge CII Best Practices Badge (Repo)
    @apiName cii-best-practices-badge-repo
    @apiGroup Risk
    @apiDescription The CII Best Practices Badge level.
                    <a href="https://github.com/chaoss/wg-risk/blob/master/focus-areas/security.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_name": "trickster",
                            "badge_level": "passing"
                        }
                    ]
    """
    server.addRepoMetric(augur_db.cii_best_practices_badge, 'cii-best-practices-badge')

    """
    @api {get} /repo-groups/:repo_group_id/forks Forks (Repo Group)
    @apiName forks-repo-group
    @apiGroup Risk
    @apiDescription A time series of fork count.
                    <a href="https://github.com/chaoss/wg-risk/blob/master/focus-areas/business-risk.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21036,
                            "repo_name": "jquery-ujs",
                            "date": "2019-07-03T23:26:42.000Z",
                            "forks": 519
                        },
                        {
                            "repo_id": 21036,
                            "repo_name": "jquery-ujs",
                            "date": "2019-07-04T16:39:39.000Z",
                            "forks": 519
                        },
                        {
                            "repo_id": 21039,
                            "repo_name": "rails_xss",
                            "date": "2019-07-03T23:26:22.000Z",
                            "forks": 20
                        },
                        {
                            "repo_id": 21039,
                            "repo_name": "rails_xss",
                            "date": "2019-07-04T16:39:20.000Z",
                            "forks": 20
                        }
                    ]
    """
    server.addRepoGroupMetric(augur_db.forks, 'forks')

    """
    @api {get} /repo-groups/:repo_group_id/repos/:repo_id/forks Forks (Repo)
    @apiName forks-repo
    @apiGroup Risk
    @apiDescription A time series of fork count.
                    <a href="https://github.com/chaoss/wg-risk/blob/master/focus-areas/business-risk.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_name": "graphiql",
                            "date": "2019-07-03T23:27:42.000Z",
                            "forks": 843
                        },
                        {
                            "repo_name": "graphiql",
                            "date": "2019-07-04T16:40:44.000Z",
                            "forks": 844
                        }
                    ]
    """
    server.addRepoMetric(augur_db.forks, 'forks')

    """
    @api {get} /repo-groups/:repo_group_id/fork-count Fork Count (Repo Group)
    @apiName fork-count-repo-group
    @apiGroup Risk
    @apiDescription Fork count.
                    <a href="https://github.com/chaoss/wg-risk/blob/master/focus-areas/business-risk.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21364,
                            "repo_name": "irs_process_scripts",
                            "forks": 4
                        },
                        {
                            "repo_id": 21420,
                            "repo_name": "ruby-coffee-script",
                            "forks": 54
                        }
                    ]
    """
    server.addRepoGroupMetric(augur_db.fork_count, 'fork-count')

    """
    @api {get} /repo-groups/:repo_group_id/repos/:repo_id/fork-count Fork Count (Repo)
    @apiName fork-count-repo
    @apiGroup Risk
    @apiDescription Fork count.
                    <a href="https://github.com/chaoss/wg-risk/blob/master/focus-areas/business-risk.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_name": "graphiql",
                            "forks": 844
                        }
                    ]
    """
    server.addRepoMetric(augur_db.fork_count, 'fork-count')

    """
    @api {get} /repo-groups/:repo_group_id/languages Languages (Repo Group)
    @apiName languages-repo-group
    @apiGroup Risk
    @apiDescription The primary language of the repository.
                    <a href="https://github.com/chaoss/wg-risk/blob/master/focus-areas/security.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21277,
                            "primary_language": "Go"
                        },
                        {
                            "repo_id": 21252,
                            "primary_language": "PHP"
                        }
                    ]
    """
    server.addRepoGroupMetric(augur_db.languages, 'languages')

    """
    @api {get} /repo-groups/:repo_group_id/languages Languages (Repo)
    @apiName languages-repo
    @apiGroup Risk
    @apiDescription The primary language of the repository.
                    <a href="https://github.com/chaoss/wg-risk/blob/master/focus-areas/security.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "primary_language":"PHP"
                        }
                    ]
    """
    server.addRepoMetric(augur_db.languages, 'languages')

    """
    @api {get} /repo-groups/:repo_group_id/license-declared License Declared (Repo Group)
    @apiName license-declared-repo-group
    @apiGroup Risk
    @apiDescription The declared software package license (fetched from CII Best Practices badging data).
                    <a href="https://github.com/chaoss/wg-risk/blob/master/focus-areas/licensing.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21252,
                            "repo_name": "php-legal-licenses",
                            "license": "Apache-2.0"
                        },
                        {
                            "repo_id": 21277,
                            "repo_name": "trickster",
                            "license": "Apache-2.0"
                        }
                    ]
    """
    server.addRepoGroupMetric(augur_db.license_declared, 'license-declared')

    """
    @api {get} /repo-groups/:repo_group_id/license-declared License Declared (Repo)
    @apiName license-declared-repo
    @apiGroup Risk
    @apiDescription The declared software package license (fetched from CII Best Practices badging data).
                    <a href="https://github.com/chaoss/wg-risk/blob/master/focus-areas/licensing.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_name":"php-legal-licenses",
                            "license": "Apache-2.0"
                        }
                    ]
    """
    server.addRepoMetric(augur_db.license_declared, 'license-declared')

    #####################################
    ###             VALUE             ###
    #####################################

    """
    @api {get} /repo-groups/:repo_group_id/stars Stars (Repo Group)
    @apiName stars-repo-group
    @apiGroup Value
    @apiDescription A time series of stars count.
    @apiParam {string} repo_group_id Repository Group ID
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21491,
                            "repo_name": "commons-io",
                            "date": "2019-07-03T23:23:36.000Z",
                            "stars": 600
                        },
                        {
                            "repo_id": 21491,
                            "repo_name": "commons-io",
                            "date": "2019-07-04T16:36:27.000Z",
                            "stars": 601
                        },
                        {
                            "repo_id": 21524,
                            "repo_name": "maven",
                            "date": "2019-07-03T23:21:14.000Z",
                            "stars": 1730
                        },
                        {
                            "repo_id": 21524,
                            "repo_name": "maven",
                            "date": "2019-07-04T16:34:04.000Z",
                            "stars": 1733
                        }
                    ]
    """
    server.addRepoGroupMetric(augur_db.stars, 'stars')

    """
    @api {get} /repo-groups/:repo_group_id/repos/:repo_id/stars Stars (Repo)
    @apiName stars-repo
    @apiGroup Value
    @apiDescription A time series of stars count.
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_name": "graphiql",
                            "date": "2019-07-03T23:27:42.000Z",
                            "stars": 8652
                        },
                        {
                            "repo_name": "graphiql",
                            "date": "2019-07-04T16:40:44.000Z",
                            "stars": 8653
                        }
                    ]
    """
    server.addRepoMetric(augur_db.stars, 'stars')

    """
    @api {get} /repo-groups/:repo_group_id/stars-count Stars Count (Repo Group)
    @apiName stars-count-repo-group
    @apiGroup Value
    @apiDescription Stars count.
    @apiParam {string} repo_group_id Repository Group ID
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_id": 21364,
                            "repo_name": "irs_process_scripts",
                            "stars": 20
                        },
                        {
                            "repo_id": 21420,
                            "repo_name": "ruby-coffee-script",
                            "stars": 19
                        }
                    ]
    """
    server.addRepoGroupMetric(augur_db.stars_count, 'stars-count')

    """
    @api {get} /repo-groups/:repo_group_id/repos/:repo_id/stars-count Stars Count (Repo)
    @apiName stars-count-repo
    @apiGroup Value
    @apiDescription Stars count.
    @apiParam {string} repo_group_id Repository Group ID.
    @apiParam {string} repo_id Repository ID.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "repo_name": "graphiql",
                            "stars": 8653
                        }
                    ]
    """
    server.addRepoMetric(augur_db.stars_count, 'stars-count')

    #####################################
    ###         EXPERIMENTAL          ###
    #####################################

    """
    @api {get} /repo-groups/:repo_group_id/lines-changed-by-author Lines Changed by Author(Repo)
    @apiNames lines-changed-by-author
    @apiGroup Experimental
    @apiDescription Returns number of lines changed per author per day
    @apiParam {string} repo_group_id Repository Group ID
    @apiParam {string} repo_id Repository ID.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "cmt_author_email": "david@loudthinking.com",
                            "cmt_author_date": "2004-11-24",
                            "affiliation": "NULL",
                            "additions": 25611,
                            "deletions": 296,
                            "whitespace": 5279
                        },
                        {
                            "cmt_author_email": "david@loudthinking.com",
                            "cmt_author_date": "2004-11-25",
                            "affiliation": "NULL",
                            "additions": 163,
                            "deletions": 179,
                            "whitespace": 46
                        }
                    ]
    """
    server.addRepoMetric(augur_db.lines_changed_by_author,'lines-changed-by-author')

    """
    @api {get} /repo-groups/:repo_group_id/lines-changed-by-author Lines Changed by Author(Repo)
    @apiNames lines-changed-by-author
    @apiGroup Experimental
    @apiDescription Count of closed issues.
                    <a href="https://github.com/chaoss/wg-evolution/blob/master/metrics/contributors-new.md">CHAOSS Metric Definition</a>
    @apiParam {string} repo_group_id Repository Group ID
    @apiParam {string} repo_id Repository ID.
    @apiSuccessExample {json} Success-Response:
                    [
                        {
                            "cmt_author_email": "david@loudthinking.com",
                            "cmt_author_date": "2004-11-24",
                            "affiliation": "NULL",
                            "additions": 25611,
                            "deletions": 296,
                            "whitespace": 5279
                        },
                        {
                            "cmt_author_email": "david@loudthinking.com",
                            "cmt_author_date": "2004-11-25",
                            "affiliation": "NULL",
                            "additions": 163,
                            "deletions": 179,
                            "whitespace": 46
                        }
                    ]
    """
    server.addRepoGroupMetric(augur_db.lines_changed_by_author,'lines-changed-by-author')


    """
    @api {get} /repo-groups/:repo_group_id/annual-commit-count-ranked-by-new-repo-in-repo-group Annual Commit Count Ranked by New Repo in Repo Group
    @apiName annual-commit-count-ranked-by-new-repo-in-repo-group
    @apiGroup Experiment
    @apiDescription This is an Augur-specific metric. We are currently working to define these more formally. Source: Git Repository
    @apiParam {String} repo_url_base Base64 version of the URL of the GitHub repository as it appears in the Facade DB
    @apiSuccessExample {json} Success-Response:
                        [
                            {
                                "repos_id": 1,
                                "net": 2479124,
                                "patches": 1,
                                "name": "twemoji"
                            },
                            {
                                "repos_id": 63,
                                "net": 2477911,
                                "patches": 1,
                                "name": "twemoji-1"
                            }
                        ]
    """
    server.addRepoGroupMetric(augur_db.annual_commit_count_ranked_by_new_repo_in_repo_group,'annual-commit-count-ranked-by-new-repo-in-repo-group')
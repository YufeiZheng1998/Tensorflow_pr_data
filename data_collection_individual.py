import requests
from github import Github
from github.GithubException import RateLimitExceededException
import csv
import logging
import calendar
import time

csv_columns = ['pr_id','pr_title','pr_body', 'requester', 'commits_messages','changed_files', 'comments', 'reviewer']
csv_file = "tensorflow_sample.csv"
g = Github("YOUR GITHUB TOKEN")
repo = g.get_repo("tensorflow/tensorflow")
closed_prs = iter(repo.get_pulls(state='closed'))
with open(csv_file, 'a+') as csvfile:
  cnt = 0
  writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
  writer.writeheader()
  while True:
    try:
      pr = next(closed_prs)
      cnt += 1
      print("Start Processing PR: {}".format(cnt))
      pr_data = {}
      pr_data['pr_id'] = pr.number
      pr_data['pr_title'] = pr.title
      pr_data['pr_body'] = pr.body
      pr_data['requester'] = pr.user.login
      r_comments = pr.get_review_comments()
      i_comments = pr.get_issue_comments()
      all_commenters = set()
      comment_docs = []
      # Commmit Messages
      commits_messages = []
      commits_comments = []
      changed_files= set()

      for commit in pr.get_commits():
        commits_messages.append(commit.commit.message)
        files = commit.files
        for f in files:
          changed_files.add(f.filename)
      pr_data['commits_messages'] = commits_messages
      pr_data['changed_files'] = list(changed_files)

      for r_comment in r_comments:
        if r_comment.user != None and 'bot' not in r_comment.user.login:
          comment_pr = pr_data.copy()
          comment_pr['reviewer'] = r_comment.user.login
          comment_pr['comments'] = r_comment.body
          writer.writerow(comment_pr)
      
      for i_comment in i_comments:
        if i_comment.user != None and 'bot' not in i_comment.user.login:
          # reviewer = i_comment.user.login
          # all_commenters.add(reviewer)
          # comment_docs.append(i_comment.body)
          comment_pr = pr_data.copy()
          comment_pr['reviewer'] = i_comment.user.login
          comment_pr['comments'] = i_comment.body
          writer.writerow(comment_pr)

      # TODO: find reviewers list
      reviews = pr.get_reviews()
      original_reviewers = []
      active_reviewers = []
      for review in reviews:
        # original_reviewers.append(review.user.login)
        if review.state == 'COMMENTED' or review.state == 'APPROVED' or review.state == 'CHANGES_REQUESTED':
          review_data = pr_data.copy()
          review_data['reviewer'] = review.user.login
          review_data['comments'] = ""
          writer.writerow(review_data)
          # active_reviewers.append(review.user.login)

    except StopIteration:
      print("finished!!!")
      break
    except RateLimitExceededException:
      search_rate_limit = g.get_rate_limit().search
      logging.info('search remaining: {}'.format(search_rate_limit.remaining))
      reset_timestamp = calendar.timegm(search_rate_limit.reset.timetuple())
      sleep_time = reset_timestamp - calendar.timegm(time.gmtime()) + 10
      logging.info("Hit Rate Limit: sleep {}".format(sleep_time))
      time.sleep(sleep_time)
      continue

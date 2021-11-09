from numpy import NaN
import requests
import pandas as pd
import re

#personal token
token = ""
headers = {
	"Authorization": "token " + token
}

##Todo
##pagenization of urls - work with all pages
##external developers - 
# check for external contributor
# i will take any contributor other than apache to be external contributor
#if resp['user']['login'] != "apache":
##optimization

def get_repos():
	df = pd.read_csv("csv/asfi_refined_50_proj.csv") 
	project_list = []
	project_list = df.pj_github_api_url
	print("No. of projects:", len(project_list))
	return project_list

def get_forks(project):
	try:
		i = 1
		response = requests.get(project+"/forks?per_page=100&page=1", headers=headers)
		while response.json():
			if response.status_code == 404:
				return []
			else:
				response = requests.get(project+f"/forks?per_page=100&page={i}", headers=headers)
				forks_url = []
				for resp in response.json(): 
					forks_url.append(resp['url'])
					print("No. of forks:", len(forks_url))
			i+=1
		return forks_url

	except Exception as e:
		print("In get_forks function")
		print('{}'.format(e))

def get_pulls(url):
	try:
		i = 1
		response = requests.get(url+"/pulls?per_page=100&page=1", headers=headers)
		
		while response.json():
			
			if response.status_code == 404:
				return []
			else:
				response = requests.get(url+f"/pulls?per_page=100&page={i}", headers=headers)
				pulls_url = []
				for resp in response.josn():
					pulls_url.append(resp['url'])
				#print("No. of pulls:", len(pulls_url))
			i+=1
		return pulls_url
			
			
	except Exception as e:
		print("In get_pulls function")
		print('{}'.format(e))
	
def get_merge_status(pull_url):
	response = requests.get(pull_url+"/merge", headers=headers)
	merge_status = response.status_code
	print(merge_status)
	return merge_status

## Metric 1 - Presence of hard forks
def check_for_hard_forks():
	df = pd.read_csv("csv/asfi_refined_50_proj.csv")
	df['has_hard_fork'] = NaN
	is_hard_fork = False

	try:
		repos = get_repos()
		for repo in repos:
			forks = get_forks(repo)
			
			for fork in forks:
				pulls_data = get_pulls(fork)
				if pulls_data == []:
					merged_pr = 0
					is_hard_fork = False
					df.loc[df['pj_github_api_url'] == repo, 'has_hard_fork'] = is_hard_fork
				else:
					for pull_request in pulls_data:
						merge_status = get_merge_status(pull_request)
						merged_pr = 0
						if merge_status == 0:
							pass
						elif merge_status == 204:
							merged_pr += 1
						elif merge_status == 404:
							pass
					if merged_pr > 2:
						is_hard_fork = True
						df.loc[df['pj_github_api_url'] == repo, 'has_hard_fork'] = is_hard_fork
						
		print(repo, is_hard_fork)
		df.to_csv("csv/asfi_refined_50_proj.csv", index=False)

	except Exception as e: 
		print("Repo Failed:", repo)
		print('{}'.format(e))
		pass

def get_comments(pull_url):
	
	response = requests.get(pull_url+"/comments?per_page=100&page=1", headers=headers).json()
	comments_list = []
	
	for resp in response: 
		comments_list.append(resp["body"])
	#print(comments_list)
	return comments_list

def pattern_matching(comment):
	
	pattern = r"(clos(e|ed|ing)|dup(licate(d)?|e)?|super(c|s)ee?ded?|obsoleted?|replaced|redundant|better(implementation|solution)|solved|fixed|done|going|addressed|already)"
	result = re.match(pattern, comment)
	duplicate_pr = 0

	if result: 
		duplicate_pr += 1
	else:
		pass
	#print(duplicate_pr)
	return duplicate_pr

## Metric 2 - Ratio of duplicate PRs
def ratio_of_duplicate_prs():
	df = pd.read_csv("csv/asfi_refined_50_proj.csv")
	df['ratio_of_duplicate_prs'] = NaN
	try: 
		repos = get_repos()
		for repo in repos:
			pulls_data = get_pulls(repo)
			total_prs = len(get_pulls(repo))

			for pull_request in pulls_data:
				comments = get_comments(pull_request)
				for comment in comments:
					duplicate_prs = pattern_matching(comment)
		
			ratio = duplicate_prs / total_prs
			df.loc[df['pj_github_api_url'] == repo, 'ratio_of_duplicate_prs'] = ratio
			print(repo, ratio)
			df.to_csv("csv/asfi_refined_50_proj.csv", index=False)

	except Exception as e: 
		print("Repo Failed:", repo)
		print('{}'.format(e))
		pass

#check_for_hard_forks()
ratio_of_duplicate_prs()

#Testing
#get_forks("https://api.github.com/repos/apache/incubator-retired-amaterasu")
#get_pulls("https://api.github.com/repos/kirupagaran/incubator-retired-amaterasu")
#total_prs = len(get_pulls("https://api.github.com/repos/apache/incubator-retired-amaterasu"))
#for comment in get_comments("https://api.github.com/repos/apache/incubator-retired-amaterasu/pulls"):
#	duplicate_prs = pattern_matching(comment)
#ratio = duplicate_prs / total_prs
#print("Ratio of dupicate PRs:", ratio)
#print("No. of pulls:", len(get_pulls("https://api.github.com/repos/apache/incubator-retired-amaterasu")))
#print("No. of comments:", len(get_comments("https://api.github.com/repos/apache/incubator-retired-amaterasu/pulls")))

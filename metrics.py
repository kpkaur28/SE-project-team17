from numpy import NaN
import requests
import csv
import json
import pandas as pd

#personal token
token = "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"
headers = {
	"Authorization": "token " + token
}

##pagenization of urls - work with all pages
##external developers - for now have set anyone other than apache to be external
##optimization

def get_repos():
	df = pd.read_csv("asfi_refined_1_proj.csv") 
	project_list = []
	project_list = df.pj_github_api_url
	print("No. of projects:", len(project_list))
	return project_list

def get_forks(project):
	try:
		resp = requests.get(project+"/forks?per_page=100&page=1", headers=headers)
		if resp.status_code == 404:
			return []
		else:
			response = requests.get(project+"/forks?per_page=100&page=1", headers=headers).json()
			url = []
			for resp in response: 
				url.append(resp['url'])
			print("No. of forks:", len(url))
			return url

	except Exception as e:
		print("In get_forks function")
		print('{}'.format(e))

def get_pulls(url):
	try:
		resp = requests.get(url+"/pulls?per_page=100&page=1", headers=headers)
		if resp.status_code == 404:
			return []
		else:
			response = requests.get(url+"/pulls?per_page=100&page=1", headers=headers).json()
			#print('fork url resp', url)
			pulls_url = []
			for resp in response:
				# check for external contributor
				# i will take any contributor other than apache to be external contributor
				if resp['user']['login'] != "apache":
					pulls_url.append(resp['url'])
				print("No. of pulls:", len(pulls_url))
			return pulls_url
			
	except Exception as e:
		print("In get_pulls function")
		print('{}'.format(e))
	
def get_merge_status(pull_url):
	response = requests.get(pull_url+"/merge", headers=headers)
	merge_status = response.status_code
	print(merge_status)
	return merge_status

def check_for_hard_forks():
	df = pd.read_csv("asfi_refined_1_proj.csv")
	df['has_hard_fork'] = NaN
	is_hard_fork = False

	try:
		repos = get_repos()
		for repo in repos:
			forks = get_forks(repo)
			
			for fork in forks:
				#print('here')
				pulls_data = get_pulls(fork)
				#print("I am after get_pulls")
				#print('here 2')
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
		df.to_csv("asfi_refined_1_proj.csv", index=False)

	except Exception as e: 
		print('{}'.format(e))
		pass

#get_forks("https://api.github.com/repos/apache/incubator-Amaterasu")
#get_pulls("https://api.github.com/repos/kirupagaran/incubator-amaterasu")
check_for_hard_forks()
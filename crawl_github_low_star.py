import requests
import time
import json
from datetime import datetime
from typing import List, Dict

class GitHubLLMScraper:
    def __init__(self, token: str):
        """
        初始化爬虫
        
        Args:
            token: GitHub Personal Access Token
                   在 https://github.com/settings/tokens 生成
                   需要 public_repo 权限
        """
        self.token = token
        self.headers = {
            "Authorization": f"token {token}",
            "Accept": "application/vnd.github.v3+json"
        }
        self.base_url = "https://api.github.com/search/repositories"
        
    def search_repos(self, query: str, page: int = 1, per_page: int = 100) -> Dict:
        """
        搜索仓库
        
        Args:
            query: 搜索查询字符串
            page: 页码
            per_page: 每页数量（最大100）
        
        Returns:
            API响应的JSON数据
        """
        params = {
            "q": query,
            "per_page": per_page,
            "page": page,
            "sort": "updated",
            "order": "desc"
        }
        
        try:
            response = requests.get(self.base_url, headers=self.headers, params=params)
            
            # 检查rate limit
            remaining = response.headers.get('X-RateLimit-Remaining')
            if remaining:
                print(f"  [Rate Limit剩余: {remaining}]", end=" ")
            
            if response.status_code == 403:
                reset_time = int(response.headers.get('X-RateLimit-Reset', 0))
                if reset_time:
                    wait_time = reset_time - time.time() + 10
                    print(f"\n⚠️  Rate limit达到上限，等待 {wait_time:.0f} 秒...")
                    time.sleep(wait_time)
                    return self.search_repos(query, page, per_page)
            
            response.raise_for_status()
            return response.json()
            
        except requests.exceptions.RequestException as e:
            print(f"\n❌ 请求错误: {e}")
            return {"items": [], "total_count": 0}
    
    def get_repos_by_stars_and_date(self, stars: int, start_date: str, end_date: str) -> List[Dict]:
        """
        按star数和日期范围获取仓库
        
        Args:
            stars: star数量
            start_date: 开始日期 (YYYY-MM-DD)
            end_date: 结束日期 (YYYY-MM-DD)
        
        Returns:
            仓库列表
        """
        query = f"topic:llm stars:{stars} created:{start_date}..{end_date}"
        print(f"    查询: {query}")
        
        all_repos = []
        page = 1
        
        while page <= 10:  # GitHub最多返回1000条（10页 × 100条）
            data = self.search_repos(query, page=page)
            
            total_count = data.get("total_count", 0)
            items = data.get("items", [])
            
            if page == 1:
                print(f"找到 {total_count} 个结果", end="")
            
            if not items:
                break
            
            all_repos.extend(items)
            print(f".", end="", flush=True)
            
            # 如果这页不满100条，说明是最后一页
            if len(items) < 100:
                break
            
            page += 1
            time.sleep(1)  # 避免触发rate limit
        
        print(f" 获取 {len(all_repos)} 条")
        return all_repos
    
    def get_all_low_star_repos(self, star_range: List[int] = [0, 1, 2]) -> List[Dict]:
        """
        获取所有低star数的LLM仓库
        
        Args:
            star_range: 要爬取的star数列表，默认 [0, 1, 2]
        
        Returns:
            所有仓库的列表（已去重）
        """
        # 定义时间分片策略
        # 根据LLM话题的流行程度，近期时间段切分更细
        date_ranges = [
            # 早期（大跨度）
            ("2008-01-01", "2017-12-31"),  # 早期
            ("2018-01-01", "2020-12-31"),  # GPT-2时代
            ("2021-01-01", "2022-06-30"),  # GPT-3早期
            ("2022-07-01", "2022-11-30"),  # ChatGPT发布前
            
            # 2022年12月 - ChatGPT发布，按月分
            ("2022-12-01", "2022-12-31"),
            
            # 2023年 - 爆发期，按月分
            ("2023-01-01", "2023-01-31"),
            ("2023-02-01", "2023-02-28"),
            ("2023-03-01", "2023-03-31"),
            ("2023-04-01", "2023-04-30"),
            ("2023-05-01", "2023-05-31"),
            ("2023-06-01", "2023-06-30"),
            ("2023-07-01", "2023-07-31"),
            ("2023-08-01", "2023-08-31"),
            ("2023-09-01", "2023-09-30"),
            ("2023-10-01", "2023-10-31"),
            ("2023-11-01", "2023-11-30"),
            ("2023-12-01", "2023-12-31"),
            
            # 2024年 - 持续火热，按半月分
            ("2024-01-01", "2024-01-15"),
            ("2024-01-16", "2024-01-31"),
            ("2024-02-01", "2024-02-15"),
            ("2024-02-16", "2024-02-29"),
            ("2024-03-01", "2024-03-15"),
            ("2024-03-16", "2024-03-31"),
            ("2024-04-01", "2024-04-15"),
            ("2024-04-16", "2024-04-30"),
            ("2024-05-01", "2024-05-15"),
            ("2024-05-16", "2024-05-31"),
            ("2024-06-01", "2024-06-15"),
            ("2024-06-16", "2024-06-30"),
            ("2024-07-01", "2024-07-15"),
            ("2024-07-16", "2024-07-31"),
            ("2024-08-01", "2024-08-15"),
            ("2024-08-16", "2024-08-31"),
            ("2024-09-01", "2024-09-15"),
            ("2024-09-16", "2024-09-30"),
            ("2024-10-01", "2024-10-15"),
            ("2024-10-16", "2024-10-31"),
            ("2024-11-01", "2024-11-15"),
            ("2024-11-16", "2024-11-30"),
            ("2024-12-01", "2024-12-15"),
            ("2024-12-16", "2024-12-31"),
            
            # 2025年 - 按周分（最新最密集）
            ("2025-01-01", "2025-01-07"),
            ("2025-01-08", "2025-01-14"),
            ("2025-01-15", "2025-01-21"),
            ("2025-01-22", "2025-01-31"),
            ("2025-02-01", "2025-02-07"),
            ("2025-02-08", "2025-02-14"),
            ("2025-02-15", "2025-02-21"),
            ("2025-02-22", "2025-02-28"),
            ("2025-03-01", "2025-03-07"),
            ("2025-03-08", "2025-03-14"),
            ("2025-03-15", "2025-03-21"),
            ("2025-03-22", "2025-03-31"),
            ("2025-04-01", "2025-04-07"),
            ("2025-04-08", "2025-04-14"),
            ("2025-04-15", "2025-04-21"),
            ("2025-04-22", "2025-04-30"),
            ("2025-05-01", "2025-05-07"),
            ("2025-05-08", "2025-05-14"),
            ("2025-05-15", "2025-05-21"),
            ("2025-05-22", "2025-05-31"),
            ("2025-06-01", "2025-06-07"),
            ("2025-06-08", "2025-06-14"),
            ("2025-06-15", "2025-06-21"),
            ("2025-06-22", "2025-06-30"),
            ("2025-07-01", "2025-07-07"),
            ("2025-07-08", "2025-07-14"),
            ("2025-07-15", "2025-07-21"),
            ("2025-07-22", "2025-07-31"),
            ("2025-08-01", "2025-08-07"),
            ("2025-08-08", "2025-08-14"),
            ("2025-08-15", "2025-08-21"),
            ("2025-08-22", "2025-08-31"),
            ("2025-09-01", "2025-09-07"),
            ("2025-09-08", "2025-09-14"),
            ("2025-09-15", "2025-09-21"),
            ("2025-09-22", "2025-09-30"),
            ("2025-10-01", "2025-10-07"),
            ("2025-10-08", "2025-10-14"),
            ("2025-10-15", "2025-10-21"),
            ("2025-10-22", "2025-10-31"),
            ("2025-11-01", "2025-11-07"),
            ("2025-11-08", "2025-11-14"),
            ("2025-11-15", "2025-11-21"),
            ("2025-11-22", "2025-11-30"),
            ("2025-12-01", "2025-12-31"),
        ]
        
        all_repos = []
        total_start = time.time()
        
        for stars in star_range:
            print(f"\n{'='*60}")
            print(f"🌟 正在爬取 {stars} star 的仓库")
            print(f"{'='*60}")
            
            star_count = 0
            
            for start_date, end_date in date_ranges:
                print(f"  📅 {start_date} ~ {end_date}: ", end="")
                
                repos = self.get_repos_by_stars_and_date(stars, start_date, end_date)
                star_count += len(repos)
                all_repos.extend(repos)
                
                time.sleep(2)  # 友好的请求间隔
            
            print(f"\n  ✅ {stars} star 共获取: {star_count} 个仓库")
        
        # 去重（按repo id）
        unique_repos = {}
        for repo in all_repos:
            repo_id = repo.get('id')
            if repo_id and repo_id not in unique_repos:
                unique_repos[repo_id] = repo
        
        total_time = time.time() - total_start
        
        print(f"\n{'='*60}")
        print(f"🎉 爬取完成！")
        print(f"{'='*60}")
        print(f"原始数据: {len(all_repos)} 条")
        print(f"去重后: {len(unique_repos)} 条")
        print(f"耗时: {total_time:.1f} 秒")
        
        return list(unique_repos.values())
    
    def save_to_json(self, repos: List[Dict], filename: str = "llm_repos.json"):
        """保存到JSON文件"""
        # 提取完整信息
        simplified_repos = []
        for repo in repos:
            owner_info = repo.get("owner", {})
            simplified_repos.append({
                "owner": owner_info.get("login"),
                "owner_url": owner_info.get("html_url"),
                "repo": repo.get("name"),
                "repo_url": repo.get("html_url"),
                "description": repo.get("description"),
                "topics": repo.get("topics", []),
                "language": repo.get("language"),
                "stars_display": repo.get("stargazers_count"),
                "stars": repo.get("stargazers_count"),
                "updated_iso": repo.get("updated_at"),
                "code_url": repo.get("html_url"),  # 代码URL就是仓库URL
                "issues_url": f"{repo.get('html_url')}/issues" if repo.get('html_url') else None,
                "pulls_url": f"{repo.get('html_url')}/pulls" if repo.get('html_url') else None,
                "discussions_url": f"{repo.get('html_url')}/discussions" if repo.get('html_url') else None,
                "sponsor_url": None,  # GitHub API不直接提供sponsor信息，需要额外请求
                # 额外有用信息
                "id": repo.get("id"),
                "full_name": repo.get("full_name"),
                "forks": repo.get("forks_count"),
                "watchers": repo.get("watchers_count"),
                "open_issues": repo.get("open_issues_count"),
                "created_at": repo.get("created_at"),
                "updated_at": repo.get("updated_at"),
                "pushed_at": repo.get("pushed_at"),
                "homepage": repo.get("homepage"),
                "size": repo.get("size"),
                "default_branch": repo.get("default_branch"),
                "license": repo.get("license", {}).get("name") if repo.get("license") else None,
                "is_fork": repo.get("fork"),
                "is_archived": repo.get("archived"),
                "is_disabled": repo.get("disabled"),
            })
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(simplified_repos, f, ensure_ascii=False, indent=2)
        
        print(f"💾 已保存到: {filename}")
    
    def save_to_csv(self, repos: List[Dict], filename: str = "llm_repos.csv"):
        """保存到CSV文件"""
        import csv
        
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                "owner", "owner_url", "repo", "repo_url", "description", "topics",
                "language", "stars_display", "stars", "updated_iso", "code_url",
                "issues_url", "pulls_url", "discussions_url", "sponsor_url",
                "forks", "watchers", "open_issues", "created_at", "license",
                "is_fork", "is_archived", "homepage"
            ])
            
            for repo in repos:
                owner_info = repo.get("owner", {})
                repo_url = repo.get("html_url")
                
                writer.writerow([
                    owner_info.get("login"),
                    owner_info.get("html_url"),
                    repo.get("name"),
                    repo_url,
                    repo.get("description", "")[:500] if repo.get("description") else "",
                    ", ".join(repo.get("topics", [])),
                    repo.get("language"),
                    repo.get("stargazers_count"),
                    repo.get("stargazers_count"),
                    repo.get("updated_at"),
                    repo_url,
                    f"{repo_url}/issues" if repo_url else "",
                    f"{repo_url}/pulls" if repo_url else "",
                    f"{repo_url}/discussions" if repo_url else "",
                    "",  # sponsor_url需要额外API
                    repo.get("forks_count"),
                    repo.get("watchers_count"),
                    repo.get("open_issues_count"),
                    repo.get("created_at"),
                    repo.get("license", {}).get("name") if repo.get("license") else "",
                    repo.get("fork"),
                    repo.get("archived"),
                    repo.get("homepage", "")
                ])
        
        print(f"💾 已保存到: {filename}")


def main():
    """主函数 - 使用示例"""
    
    # ⚠️ 请替换为你的GitHub Token
    # 生成地址: https://github.com/settings/tokens
    TOKEN = "XXXX"
    
    if TOKEN == "your_github_token_here":
        print("❌ 请先设置你的GitHub Token！")
        print("📝 生成地址: https://github.com/settings/tokens")
        print("   需要勾选 'public_repo' 权限")
        return
    
    # 创建爬虫实例
    scraper = GitHubLLMScraper(TOKEN)
    
    # 爬取 0, 1, 2 star 的仓库
    repos = scraper.get_all_low_star_repos(star_range=[2])
    
    # 保存结果
    scraper.save_to_json(repos, "llm_low_star_repos.json")
    scraper.save_to_csv(repos, "llm_low_star_repos.csv")
    
    # 统计信息
    print(f"\n📊 统计信息:")
    stars_count = {}
    for repo in repos:
        stars = repo.get("stargazers_count", 0)
        stars_count[stars] = stars_count.get(stars, 0) + 1
    
    for stars in sorted(stars_count.keys()):
        print(f"   {stars} star: {stars_count[stars]} 个仓库")


if __name__ == "__main__":
    main()
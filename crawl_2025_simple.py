#!/usr/bin/env python3
"""
Simple AoPS 2025 Crawler
Crawls AoPS topics from 2025 directly using requests.
"""

import requests
import json
import datetime
import time
import argparse
import os
from tqdm import tqdm

class AOPSCrawler:
    def __init__(self):
        self.session = requests.Session()
        self.session_id = None
        self._refresh_session()

    def _refresh_session(self):
        """Get fresh session credentials from AoPS"""
        resp = self.session.get('https://artofproblemsolving.com/community', timeout=30)
        content = resp.text
        idx = content.find('AoPS.session =')
        if idx != -1:
            start = content.find('{', idx)
            end = content.find('}', start) + 1
            session_json = json.loads(content[start:end])
            self.session_id = session_json['id']
        print(f"Session refreshed: {self.session_id[:16]}...")

    def get_topic(self, topic_id):
        """Fetch a single topic by ID"""
        url = 'https://artofproblemsolving.com/m/community/ajax.php'
        data = {
            'topic_fetch': 'initial',
            'new_topic_id': str(topic_id),
            'fetch_first': '1',
            'fetch_all': '1',
            'a': 'change_focus_topic',
            'aops_logged_in': 'false',
            'aops_user_id': '1',
            'aops_session_id': self.session_id,
        }
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'Accept': 'application/json',
        }

        try:
            resp = self.session.post(url, data=data, headers=headers, timeout=30)
            if resp.status_code == 200:
                return resp.json()
            else:
                return {'error_code': f'HTTP_{resp.status_code}'}
        except Exception as e:
            return {'error_code': str(e)}

    def get_topic_date(self, result):
        """Extract first post date from topic result"""
        try:
            if 'response' in result and 'posts' in result['response']:
                posts = result['response']['posts']
                if posts:
                    return datetime.datetime.fromtimestamp(posts[0]['post_time'])
        except:
            pass
        return None

    def crawl(self, start_id, end_id, output_path, delay=0.5):
        """Crawl topics from start_id to end_id"""
        # Load already crawled IDs
        crawled_ids = set()
        if os.path.exists(output_path):
            with open(output_path, 'r') as f:
                for line in f:
                    try:
                        data = json.loads(line)
                        crawled_ids.add(data['topic_id'])
                    except:
                        pass
            print(f"Resuming: {len(crawled_ids)} topics already crawled")

        # Open output file in append mode
        outfile = open(output_path, 'a')

        session_refresh_counter = 0
        success_count = 0
        error_count = 0

        pbar = tqdm(range(start_id, end_id + 1), desc="Crawling")
        for topic_id in pbar:
            if topic_id in crawled_ids:
                continue

            # Refresh session every 500 requests
            session_refresh_counter += 1
            if session_refresh_counter >= 500:
                self._refresh_session()
                session_refresh_counter = 0

            result = self.get_topic(topic_id)

            # Write result
            output = {
                'topic_id': topic_id,
                'response': result
            }
            outfile.write(json.dumps(output) + '\n')
            outfile.flush()

            # Check if successful
            if 'error_code' not in result:
                success_count += 1
                date = self.get_topic_date(result)
                if date:
                    pbar.set_postfix({
                        'date': date.strftime('%Y-%m-%d'),
                        'ok': success_count,
                        'err': error_count
                    })
            else:
                error_count += 1

            time.sleep(delay)

        outfile.close()
        print(f"\nDone! Success: {success_count}, Errors: {error_count}")


def main():
    parser = argparse.ArgumentParser(description='Crawl AoPS 2025 topics')
    parser.add_argument('--start', type=int, default=3470000,
                        help='Starting topic ID (default: 3470000 for ~Jan 2025)')
    parser.add_argument('--end', type=int, default=3600000,
                        help='Ending topic ID (default: 3600000)')
    parser.add_argument('--output', type=str, default='out/items_raw_2025.jl',
                        help='Output file path')
    parser.add_argument('--delay', type=float, default=0.3,
                        help='Delay between requests in seconds')
    args = parser.parse_args()

    # Create output directory
    os.makedirs(os.path.dirname(args.output), exist_ok=True)

    print(f"AoPS 2025 Crawler")
    print(f"  Start ID: {args.start}")
    print(f"  End ID: {args.end}")
    print(f"  Output: {args.output}")
    print(f"  Delay: {args.delay}s")
    print()

    crawler = AOPSCrawler()
    crawler.crawl(args.start, args.end, args.output, args.delay)


if __name__ == '__main__':
    main()

# --- 必要なライブラリの読み込み ---
from urllib.parse import urljoin
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
import requests


def main():
  # 1. 湘南ベルマーレの総合新着・ニュースページ
  target_url = "https://www.bellmare.co.jp/category/all/"
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
      )
  }

  # 2. ページHTMLの取得
  response = requests.get(target_url, headers=headers)
  response.encoding = response.apparent_encoding
  soup = BeautifulSoup(response.text, "html.parser")

  # 3. RSSの土台作成
  fg = FeedGenerator()
  fg.title("湘南ベルマーレ 新着ニュース")
  fg.link(href=target_url, rel="alternate")
  fg.description(
      "湘南ベルマーレ公式サイト（https://www.bellmare.co.jp/category/all/）の自動生成RSS"
  )
  fg.language("ja")

  # 4. 記事のブロック（WordPress等でよく使われる article やリスト要素）を探索
  # 公式サイトの構造に合わせて柔軟に記事リンクを抽出します
  articles = soup.find_all(["article", "div"], class_ = lambda x: x and ("post" in x or "item" in x or "news" in x))
  
  # もし上記でうまく取れない場合のフォールバックとして、一般的なaタグの構造も考慮
  if not articles:
    articles = soup.find_all("a", href=True)

  added_urls = set()

  for item in articles:
    # article要素の場合は内部のリンクとタイトルを探す
    if item.name == "article":
      link_tag = item.find("a", href=True)
      if not link_tag:
        continue
      href = link_tag["href"]
      # タイトルはh2, h3、あるいはリンクのテキストから取得
      title_tag = item.find(["h2", "h3", "h4", "p"])
      title = title_tag.get_text(strip=True) if title_tag else link_tag.get_text(strip=True)
      
      # 日付があれば取得
      time_tag = item.find("time")
      date_str = time_tag.get_text(strip=True) if time_tag else ""
    else:
      # aタグ直接の場合
      href = item.get("href")
      if not href or "/news/" not in href: # ニュース記事っぽいURLに絞る
        continue
      title = item.get_text(strip=True)
      date_str = ""

    if not href or not title:
      continue

    full_url = urljoin(target_url, href)

    if full_url in added_urls or "category/all" in full_url:
      continue

    added_urls.add(full_url)

    # RSSエントリーの追加
    fe = fg.add_entry()
    fe.title(f"{date_str} {title}".strip() if date_str else title)
    fe.link(href=full_url)
    fe.guid(full_url, permalink=True)

  # 5. bellmare.xml ファイルとして保存
  fg.rss_file("bellmare.xml")
  print("bellmare.xml の作成が完了しました。")


if __name__ == "__main__":
  main()

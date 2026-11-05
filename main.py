from urllib.parse import urljoin
from bs4 import BeautifulSoup
from feedgen.feed import FeedGenerator
import requests


def main():
  target_url = "https://www.bellmare.co.jp/category/all/"
  headers = {
      "User-Agent": (
          "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
      )
  }

  response = requests.get(target_url, headers=headers)
  response.encoding = response.apparent_encoding
  soup = BeautifulSoup(response.text, "html.parser")

  fg = FeedGenerator()
  fg.title("湘南ベルマーレ 新着ニュース")
  fg.link(href=target_url, rel="alternate")
  fg.description("湘南ベルマーレ公式サイトの自動生成RSS")
  fg.language("ja")

  # ニュース一覧ページ内にあるすべてのリンクを探索し、ニュース記事のURL（'/news/'等を含むもの）を対象にする
  # ベルマーレ公式サイトの構造に合わせて柔軟に抽出します
  added_urls = set()

  # 記事リストを囲む要素や、<a>タグの中からニュース詳細へのリンクを探す
  for a_tag in soup.find_all("a", href=True):
    href = a_tag["href"]

    # ベルマーレのニュース記事URLによく含まれるパターン、または特定のパスに絞る
    # （例: /news/ や個別記事の構造に合わせて調整）
    if "/news/" not in href and "/wp/" not in href:  # 必要に応じて調整
      # もし上記で弾かれすぎる場合は、ドメイン内かつカテゴリページ以外を広く拾う
      pass

    title = a_tag.get_text(strip=True)

    # タイトルが短すぎるものや、ナビゲーション用のリンク、画像だけのものは除外
    if not title or len(title) < 5:
      continue

    full_url = urljoin(target_url, href)

    # サイト内の別カテゴリや重複、トップページ自体は除外
    if full_url in added_urls or target_url == full_url:
      continue

    # ベルマーレのドメイン内の記事であること、かつカテゴリ一覧ページではないこと
    if "bellmare.co.jp" in full_url and "category" not in full_url:
      added_urls.add(full_url)

      fe = fg.add_entry()
      fe.title(title)
      fe.link(href=full_url)
      fe.guid(full_url, permalink=True)

  fg.rss_file("bellmare.xml")
  print("bellmare.xml の生成が完了しました。")


if __name__ == "__main__":
  main()

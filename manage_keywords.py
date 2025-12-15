"""Utility script to manage keywords database."""

import sys
from aegis.keyword_db import KeywordDatabase


def main():
    keyword_db = KeywordDatabase(db_path="keywords.json")
    
    if len(sys.argv) < 2:
        print("\nUsage: python manage_keywords.py <command>")
        print("\nCommands:")
        print("  stats    - Show database statistics")
        print("  validate - Validate database")
        print("  list     - List all keywords")
        print("  domain <name> - Show keywords for specific domain")
        print("  format   - Format keywords for discovery agent\n")
        return
    
    command = sys.argv[1].lower()
    
    if command == "stats":
        keyword_db.stats()
    
    elif command == "validate":
        validation = keyword_db.validate()
        print("\n" + "="*60)
        print("VALIDATION")
        print("="*60)
        print(f"Status: {'✓ Valid' if validation['is_valid'] else '❌ Invalid'}")
        
        if validation['errors']:
            print("\nErrors:")
            for error in validation['errors']:
                print(f"  ❌ {error}")
        
        if validation['warnings']:
            print("\nWarnings:")
            for warning in validation['warnings']:
                print(f"  ⚠️ {warning}")
        
        stats = validation['stats']
        print(f"\nTotal domains: {stats['total_domains']}")
        print(f"Total keywords: {stats['total_keywords']}")
        print("="*60 + "\n")
    
    elif command == "list":
        all_keywords = keyword_db.get_all_keywords()
        if not all_keywords:
            print("\n❌ No keywords found!\n")
            return
        
        print("\n" + "="*60)
        print("ALL KEYWORDS BY DOMAIN")
        print("="*60 + "\n")
        
        for domain, keywords in sorted(all_keywords.items()):
            print(f"\n{domain} ({len(keywords)} keywords):")
            print("-" * 60)
            for i, kw in enumerate(keywords, 1):
                print(f"  {i:3d}. {kw}")
        print("\n" + "="*60 + "\n")
    
    elif command == "domain":
        if len(sys.argv) < 3:
            print("\n❌ Error: Specify domain name")
            print("   Usage: python manage_keywords.py domain <domain_name>\n")
            return
        
        domain = sys.argv[2]
        keywords = keyword_db.get_domain_keywords(domain)
        
        if not keywords:
            print(f"\n❌ No keywords for: {domain}")
            print(f"Available: {', '.join(keyword_db.list_domains())}\n")
            return
        
        print(f"\n{domain} ({len(keywords)} keywords):")
        print("="*60)
        for i, kw in enumerate(keywords, 1):
            print(f"  {i:3d}. {kw}")
        print("="*60 + "\n")
    
    elif command == "format":
        formatted = keyword_db.format_for_discovery_agent()
        print("\n" + "="*60)
        print("FORMATTED FOR DISCOVERY AGENT")
        print("="*60 + "\n")
        print(formatted)
    
    else:
        print(f"\n❌ Unknown command: {command}\n")


if __name__ == "__main__":
    main()

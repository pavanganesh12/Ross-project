from Opportunity_Discovery_Workflow.Agents.simpler_grants_gov_agent import get_agent as get_fetch_agent_simpler
from Opportunity_Discovery_Workflow.Agents.grants_gov_agent import get_agent as get_fetch_agent_grants_gov
from Opportunity_Discovery_Workflow.Agents.sam_gov_agent import get_agent as get_fetch_agent_sam_gov
from Opportunity_Discovery_Workflow.Agents.aggregation_agent import get_agent as get_aggregation_agent
from Opportunity_Discovery_Workflow.Agents.filter_agent import get_agent as get_filter_agent
from Opportunity_Discovery_Workflow.Agents.scoring_agent import get_agent as get_scoring_agent
from Opportunity_Discovery_Workflow.Agents.report_agent import get_agent as get_report_agent
from Opportunity_Discovery_Workflow.Models.data_models import OpportunityList, ScoredOpportunityList
from Opportunity_Discovery_Workflow.utils.pdf_converter import convert_md_to_pdf
import os
import json
from datetime import datetime

class DiscoveryWorkflow:
    def __init__(self):
        print("Initializing Simple Grants Workflow...")
        self.fetch_agent_simpler = get_fetch_agent_simpler()
        self.fetch_agent_grants_gov = get_fetch_agent_grants_gov()
        self.fetch_agent_sam_gov = get_fetch_agent_sam_gov()
        self.aggregation_agent = get_aggregation_agent()
        self.filter_agent = get_filter_agent()
        self.scoring_agent = get_scoring_agent()
        self.report_agent = get_report_agent()
        
        self.base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.output_dir = os.path.join(self.base_path, "outputs")
        os.makedirs(self.output_dir, exist_ok=True)

    def run(self):
        print("\n" + "="*70)
        print("SIMPLE GRANTS WORKFLOW - START")
        print("="*70)
        
        print("\n--- PHASE 1: FETCH ALL OPPORTUNITIES ---")
        all_opportunities = self._fetch_opportunities()
        if not all_opportunities:
            print("⚠️ No opportunities fetched. Workflow terminated.")
            return
        
        print("\n--- PHASE 2: AGGREGATE OPPORTUNITIES ---")
        aggregated_opportunities = self._aggregate_opportunities(all_opportunities)
        if not aggregated_opportunities:
            print("⚠️ Aggregation failed. Workflow terminated.")
            return

        print("\n--- PHASE 3: FILTER BY DOMAINS/KEYWORDS ---")
        filtered_opportunities = self._filter_opportunities(aggregated_opportunities)
        if not filtered_opportunities:
            print("⚠️ No opportunities matched keywords. Workflow terminated.")
            return
        
        print("\n--- PHASE 4: SCORE OPPORTUNITIES ---")
        scored_opportunities = self._score_opportunities(filtered_opportunities)
        if not scored_opportunities:
            print("⚠️ Scoring failed. Workflow terminated.")
            return
        
        print("\n--- PHASE 5: GENERATE REPORT ---")
        self._generate_report(scored_opportunities)
        
        print("\n" + "="*70)
        print("SIMPLE GRANTS WORKFLOW - COMPLETED")
        print("="*70)

    def _fetch_opportunities(self):
        all_opps = []
        
        try:
            print("🔍 Fetching from Simpler.Grants.gov...")
            response = self.fetch_agent_simpler.run(
                "Fetch opportunities posted in the last 7 days.",
                response_model=OpportunityList
            )
            if response.content and not isinstance(response.content, str):
                opps = response.content.opportunities
                print(f"   ✅ Simpler.Grants.gov: {len(opps)} opportunities")
                all_opps.extend(opps)
            else:
                print("   ⚠️ Simpler.Grants.gov: No structured data")
        except Exception as e:
            print(f"   ❌ Simpler.Grants.gov Error: {e}")

        try:
            print("🔍 Fetching from Grants.gov...")
            response = self.fetch_agent_grants_gov.run(
                "Fetch opportunities posted in the last 7 days.",
                response_model=OpportunityList
            )
            if response.content and not isinstance(response.content, str):
                opps = response.content.opportunities
                print(f"   ✅ Grants.gov: {len(opps)} opportunities")
                all_opps.extend(opps)
            else:
                print("   ⚠️ Grants.gov: No structured data")
        except Exception as e:
            print(f"   ❌ Grants.gov Error: {e}")

        try:
            print("🔍 Fetching from SAM.gov...")
            response = self.fetch_agent_sam_gov.run(
                "Fetch opportunities posted in the last 7 days.",
                response_model=OpportunityList
            )
            if response.content and not isinstance(response.content, str):
                opps = response.content.opportunities
                print(f"   ✅ SAM.gov: {len(opps)} opportunities")
                all_opps.extend(opps)
            else:
                print("   ⚠️ SAM.gov: No structured data")
        except Exception as e:
            print(f"   ❌ SAM.gov Error: {e}")

        print(f"\n✅ Total fetched: {len(all_opps)}")
        return all_opps

    def _aggregate_opportunities(self, opportunities):
        try:
            print(f"🔄 Aggregating {len(opportunities)} opportunities...")
            opps_json = json.dumps([opp.model_dump() for opp in opportunities], indent=2)
            
            response = self.aggregation_agent.run(
                f"Here is the list of opportunities:\n{opps_json}\n\n"
                f"Merge duplicates, remove redundant information, and enrich descriptions.",
                response_model=OpportunityList
            )
            
            if response.content and not isinstance(response.content, str):
                aggregated = response.content.opportunities
                print(f"✅ Aggregation complete: {len(aggregated)} unique (from {len(opportunities)} raw)")
                return aggregated
            else:
                return self._deduplicate(opportunities)
                
        except Exception as e:
            print(f"❌ Error in aggregation: {e}")
            return opportunities

    def _deduplicate(self, opportunities):
        unique_opps = {}
        for opp in opportunities:
            key = opp.url or opp.title
            if key not in unique_opps:
                unique_opps[key] = opp
        print(f"   Basic deduplication: {len(unique_opps)} opportunities")
        return list(unique_opps.values())

    def _filter_opportunities(self, opportunities):
        try:
            keywords_path = r"d:\Agno\keywords.json"
            try:
                with open(keywords_path, 'r', encoding='utf-8') as f:
                    keywords_data = json.load(f)
                    domains = list(keywords_data.get('keywords', {}).keys())
                    domain_count = len(domains)
            except Exception:
                domains = []
                domain_count = 0

            print(f"🔍 Filtering {len(opportunities)} opportunities by {domain_count} domains...")
            
            batch_size = 10
            filtered_opportunities = []
            total_batches = (len(opportunities) + batch_size - 1) // batch_size
            
            for i in range(0, len(opportunities), batch_size):
                batch = opportunities[i:i + batch_size]
                batch_num = i // batch_size + 1
                print(f"   Processing batch {batch_num}/{total_batches}...")
                
                opps_json = json.dumps([opp.model_dump() for opp in batch], indent=2)
                
                try:
                    response = self.filter_agent.run(
                        f"Filter these opportunities:\n\n{opps_json}\n\n"
                        f"Only keep opportunities matching keywords. Assign appropriate sector.",
                        response_model=OpportunityList
                    )
                    
                    if response.content and not isinstance(response.content, str):
                        filtered_opportunities.extend(response.content.opportunities)
                except Exception as e:
                    print(f"     ❌ Batch {batch_num} error: {e}")
            
            print(f"✅ Filtered to {len(filtered_opportunities)} relevant opportunities")
            
            if filtered_opportunities:
                domain_counts = {}
                for opp in filtered_opportunities:
                    sector = opp.sector or "Unknown"
                    domain_counts[sector] = domain_counts.get(sector, 0) + 1
                
                print("   Domain breakdown:")
                for domain, count in sorted(domain_counts.items(), key=lambda x: x[1], reverse=True):
                    print(f"     - {domain}: {count}")
            
            return filtered_opportunities
                
        except Exception as e:
            print(f"❌ Error in filter phase: {e}")
            return []

    def _score_opportunities(self, opportunities):
        try:
            print(f"📊 Scoring {len(opportunities)} opportunities...")
            opps_json = json.dumps([opp.model_dump() for opp in opportunities], indent=2)
            
            response = self.scoring_agent.run(
                f"Here is the list of opportunities:\n{opps_json}\n\nScore and rank them.",
                response_model=ScoredOpportunityList
            )
            
            if response.content and not isinstance(response.content, str):
                scored = response.content.opportunities
                print(f"✅ Scored {len(scored)} opportunities")
                
                if scored:
                    scores = [opp.total_score for opp in scored]
                    print(f"   Score range: {min(scores):.2f} - {max(scores):.2f} (avg: {sum(scores)/len(scores):.2f})")
                
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                scored_filepath = os.path.join(self.output_dir, f"simple_grants_scored_{timestamp}.json")
                
                with open(scored_filepath, "w", encoding="utf-8") as f:
                    json.dump([opp.model_dump() for opp in scored], f, indent=2)
                
                return scored
            else:
                print("❌ Unexpected response format")
                return []
                
        except Exception as e:
            print(f"❌ Error in scoring: {e}")
            return []

    def _generate_report(self, scored_opportunities):
        try:
            print(f"📝 Generating report for {len(scored_opportunities)} opportunities...")
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            data_filename = f"simple_grants_report_data_{timestamp}.json"
            data_filepath = os.path.join(self.output_dir, data_filename)
            report_filename = f"Simple_Grants_Report_{timestamp}.md"
            report_filepath = os.path.join(self.output_dir, report_filename)
            
            with open(data_filepath, "w", encoding="utf-8") as f:
                json.dump([opp.model_dump() for opp in scored_opportunities], f, indent=2)
            
            self.report_agent.run(
                f"Read '{data_filepath}' and generate a comprehensive Markdown report. Save as '{report_filepath}'."
            )
            
            print(f"✅ Report saved to: {report_filename}")
            
            if os.path.exists(data_filepath):
                os.remove(data_filepath)
            
            print("\n--- PHASE 6: CONVERT TO PDF ---")
            self._convert_to_pdf(report_filepath)
            
        except Exception as e:
            print(f"❌ Error in report generation: {e}")

    def _convert_to_pdf(self, md_filepath):
        try:
            print("📄 Converting to PDF...")
            pdf_filepath = convert_md_to_pdf(md_filepath)
            
            if pdf_filepath:
                print(f"✅ PDF saved to: {os.path.basename(pdf_filepath)}")
            else:
                print("⚠️ PDF conversion failed.")
        except Exception as e:
            print(f"❌ Error in PDF conversion: {e}")

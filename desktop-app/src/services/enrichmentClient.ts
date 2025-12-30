export interface EnrichmentData {
    email?: string;
    phone?: string;
    linkedin_id?: string;
    source: 'ContactOut' | 'SalesQL' | 'Manual';
}

class EnrichmentClient {
    private apiKeyContactOut: string | null = null;
    private apiKeySalesQL: string | null = null;

    setApiKeys(keys: { contactOut?: string; salesQL?: string }) {
        if (keys.contactOut) this.apiKeyContactOut = keys.contactOut;
        if (keys.salesQL) this.apiKeySalesQL = keys.salesQL;
    }

    async enrichCandidate(candidateId: string, linkedinUrl: string): Promise<EnrichmentData> {
        console.log(`Enriching candidate ${candidateId} via ${linkedinUrl}`);

        // Mocking API delay
        await new Promise(resolve => setTimeout(resolve, 1500));

        // Placeholder logic: If keys are present, pretend to fetch. Otherwise return empty.
        if (!this.apiKeyContactOut && !this.apiKeySalesQL) {
            return {
                source: 'Manual'
            };
        }

        // Return mock data
        return {
            email: `contact_${candidateId.substring(0, 5)}@example.com`,
            phone: '+1 (555) 012-3456',
            linkedin_id: linkedinUrl.split('/').pop(),
            source: this.apiKeyContactOut ? 'ContactOut' : 'SalesQL'
        };
    }
}

export const enrichmentClient = new EnrichmentClient();

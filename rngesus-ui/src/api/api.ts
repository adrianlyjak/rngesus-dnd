import z from "zod";
let API_URL = import.meta.env.PUBLIC_API_URL || "";

async function handleResponse(response: Promise<Response>): Promise<any> {
  const res = await response;
  if (res.status > 299) {
    const text = await res.text();
    const summary = text.slice(0, 100) + (text.length > 100 ? "..." : "");

    throw new Error(`${res.status}: ${res.statusText} - summary: ${summary}`)
  }
  return res.json();

}

export const CampaignSummary = z.object({
  id: z.number(),
  title: z.string().or(z.null()),
  summary: z.string().or(z.null()),
});

export type CampaignSummary = z.infer<typeof CampaignSummary>;

export const CampaignSummaryList = z.object({
  items: z.array(CampaignSummary),
});

export type CampaignSummaryList = z.infer<typeof CampaignSummaryList>;

export async function getCampaigns(): Promise<CampaignSummaryList> {
  // const apiUrl = 'https://randomuser.me/api/'
  const apiUrl = API_URL + "/api/campaigns";
  console.log(apiUrl);
  const res = await handleResponse(fetch(apiUrl));
  // return res;
  const items = CampaignSummaryList.parse(res);
  return items;
}


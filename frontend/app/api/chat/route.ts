import type { NextRequest } from "next/server"

export async function POST(req: NextRequest) {
    try {
        const body = await req.json()
        const { messages, region = "us", stream_mode = ["messages", "state"] } = body

        const API_URL = process.env.AGENT_API_URL!
        const API_KEY = process.env.AGENT_API_KEY!

        const response = await fetch(API_URL, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${API_KEY}`
            },
            body: JSON.stringify({
                messages,
                region,
                stream_mode,
            }),
        })

        if (!response.ok) {
            throw new Error(`API error: ${response.status}`)
        }

        return new Response(response.body, {
            headers: {
                "Content-Type": "text/event-stream",
                "Cache-Control": "no-cache",
                Connection: "keep-alive",
            },
        })

    } catch (error) {
        console.error("Proxy error:", error)
        return new Response(JSON.stringify({ error: "Failed to connect to agent" }), {
            status: 500,
            headers: { "Content-Type": "application/json" },
        })
    }
}

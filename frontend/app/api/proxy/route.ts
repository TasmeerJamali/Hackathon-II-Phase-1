/**
 * API Proxy for Backend Calls
 * 
 * This proxies requests to the HTTP backend from the HTTPS frontend
 * to avoid Mixed Content browser security blocks.
 * 
 * POST /api/proxy
 * Body: { endpoint: string, method: string, body?: object }
 */

import { NextRequest, NextResponse } from "next/server";

export const runtime = "nodejs";
export const dynamic = "force-dynamic";

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || "http://135.235.248.0";

export async function POST(request: NextRequest) {
    console.log("=== PROXY REQUEST START ===");
    console.log("BACKEND_URL:", BACKEND_URL);

    try {
        const requestBody = await request.json();
        const { endpoint, method = "GET", body } = requestBody;
        console.log("Request:", { endpoint, method, hasBody: !!body });

        if (!endpoint) {
            console.log("Error: No endpoint provided");
            return NextResponse.json({ error: "Endpoint required" }, { status: 400 });
        }

        const url = `${BACKEND_URL}${endpoint}`;
        console.log(`Proxying ${method} to: ${url}`);

        const options: RequestInit = {
            method,
            headers: {
                "Content-Type": "application/json",
            },
        };

        // Get auth token from request headers
        const authHeader = request.headers.get("Authorization");
        console.log("Auth header present:", !!authHeader);
        if (authHeader) {
            options.headers = {
                ...options.headers,
                "Authorization": authHeader,
            };
        }

        if (body && method !== "GET") {
            options.body = JSON.stringify(body);
            console.log("Request body:", JSON.stringify(body).substring(0, 200));
        }

        console.log("Fetching backend...");
        const response = await fetch(url, options);
        console.log("Backend response status:", response.status);

        // Handle no content
        if (response.status === 204) {
            return new NextResponse(null, { status: 204 });
        }

        const data = await response.json().catch((e) => {
            console.log("JSON parse error:", e.message);
            return {};
        });
        console.log("Response data:", JSON.stringify(data).substring(0, 200));

        console.log("=== PROXY REQUEST END ===");
        return NextResponse.json(data, { status: response.status });
    } catch (error) {
        console.error("=== PROXY ERROR ===");
        console.error("Error type:", error instanceof Error ? error.constructor.name : typeof error);
        console.error("Error message:", error instanceof Error ? error.message : String(error));
        console.error("Full error:", error);
        return NextResponse.json(
            { error: error instanceof Error ? error.message : "Proxy request failed" },
            { status: 500 }
        );
    }
}

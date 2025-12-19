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
    try {
        const { endpoint, method = "GET", body } = await request.json();

        if (!endpoint) {
            return NextResponse.json({ error: "Endpoint required" }, { status: 400 });
        }

        const url = `${BACKEND_URL}${endpoint}`;
        console.log(`Proxying ${method} request to: ${url}`);

        const options: RequestInit = {
            method,
            headers: {
                "Content-Type": "application/json",
            },
        };

        // Get auth token from request headers
        const authHeader = request.headers.get("Authorization");
        if (authHeader) {
            options.headers = {
                ...options.headers,
                "Authorization": authHeader,
            };
        }

        if (body && method !== "GET") {
            options.body = JSON.stringify(body);
        }

        const response = await fetch(url, options);
        
        // Handle no content
        if (response.status === 204) {
            return new NextResponse(null, { status: 204 });
        }

        const data = await response.json().catch(() => ({}));
        
        return NextResponse.json(data, { status: response.status });
    } catch (error) {
        console.error("Proxy error:", error);
        return NextResponse.json(
            { error: error instanceof Error ? error.message : "Proxy request failed" },
            { status: 500 }
        );
    }
}

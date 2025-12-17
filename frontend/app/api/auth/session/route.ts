/**
 * Session API Route
 * GET /api/auth/session
 */

import { NextRequest, NextResponse } from "next/server";
import { jwtVerify } from "jose";

const AUTH_SECRET = process.env.BETTER_AUTH_SECRET || "hackathon-secret-key-2024";
const SECRET_KEY = new TextEncoder().encode(AUTH_SECRET);

export async function GET(request: NextRequest) {
    try {
        const token = request.cookies.get("auth_token")?.value;

        if (!token) {
            return NextResponse.json({ session: null });
        }

        const { payload } = await jwtVerify(token, SECRET_KEY);

        return NextResponse.json({
            session: {
                user: {
                    id: payload.sub,
                    email: payload.email,
                    name: payload.name,
                },
            },
        });
    } catch {
        return NextResponse.json({ session: null });
    }
}

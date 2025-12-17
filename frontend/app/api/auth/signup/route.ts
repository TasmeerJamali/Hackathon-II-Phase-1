/**
 * Signup API Route
 * POST /api/auth/signup
 * 
 * Note: This uses in-memory storage which resets on each serverless cold start.
 * For hackathon demo purposes - production would use a database.
 */

import { NextRequest, NextResponse } from "next/server";
import { SignJWT } from "jose";

const AUTH_SECRET = process.env.BETTER_AUTH_SECRET || "hackathon-secret-key-2024";
const SECRET_KEY = new TextEncoder().encode(AUTH_SECRET);

// Simple in-memory store (resets on cold start - fine for demo)
const users = new Map<string, { id: string; email: string; name: string; password: string }>();

async function signToken(payload: { sub: string; email: string; name: string }): Promise<string> {
    return new SignJWT(payload)
        .setProtectedHeader({ alg: "HS256" })
        .setIssuedAt()
        .setExpirationTime("7d")
        .sign(SECRET_KEY);
}

export async function POST(request: NextRequest) {
    try {
        const body = await request.json();
        const { email, password, name } = body;

        if (!email || !password) {
            return NextResponse.json({ message: "Email and password required" }, { status: 400 });
        }

        // Always allow signup (serverless resets state anyway)
        const userId = `user_${Date.now()}`;
        users.set(email, { id: userId, email, name: name || email, password });

        const token = await signToken({ sub: userId, email, name: name || email });

        const response = NextResponse.json({
            user: { id: userId, email, name: name || email },
            token,
        });

        response.cookies.set("auth_token", token, {
            httpOnly: true,
            secure: process.env.NODE_ENV === "production",
            sameSite: "lax",
            maxAge: 60 * 60 * 24 * 7,
        });

        return response;
    } catch (error) {
        console.error("Signup error:", error);
        return NextResponse.json({ message: "Server error" }, { status: 500 });
    }
}

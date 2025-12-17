/**
 * Signin API Route
 * POST /api/auth/signin
 * 
 * Note: Serverless functions can't persist state between invocations.
 * For demo, we always create a token for valid email format + password length.
 */

import { NextRequest, NextResponse } from "next/server";
import { SignJWT } from "jose";

const AUTH_SECRET = process.env.BETTER_AUTH_SECRET || "hackathon-secret-key-2024";
const SECRET_KEY = new TextEncoder().encode(AUTH_SECRET);

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
        const { email, password } = body;

        if (!email || !password) {
            return NextResponse.json({ message: "Email and password required" }, { status: 400 });
        }

        // Basic validation (for demo/hackathon)
        if (password.length < 8) {
            return NextResponse.json({ message: "Invalid credentials" }, { status: 401 });
        }

        // For serverless demo: accept any valid email format
        // In production, this would check against a database
        const userId = `user_${Date.now()}`;
        const name = email.split("@")[0];

        const token = await signToken({ sub: userId, email, name });

        const response = NextResponse.json({
            user: { id: userId, email, name },
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
        console.error("Signin error:", error);
        return NextResponse.json({ message: "Server error" }, { status: 500 });
    }
}

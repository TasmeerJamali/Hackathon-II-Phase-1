/**
 * Signin API Route - With JWT
 * POST /api/auth/signin
 * 
 * Generates proper JWT tokens for AKS backend authentication
 */

import { NextRequest, NextResponse } from "next/server";
import { SignJWT } from "jose";

// Explicitly use Node.js runtime
export const runtime = "nodejs";
export const dynamic = "force-dynamic";

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
    console.log("Signin route called");

    try {
        const body = await request.json();
        console.log("Request body:", JSON.stringify(body));

        const { email, password } = body;

        if (!email || !password) {
            return NextResponse.json({ message: "Email and password required" }, { status: 400 });
        }

        // For demo: accept any valid email/password (min 8 chars)
        if (password.length < 8) {
            return NextResponse.json({ message: "Invalid credentials" }, { status: 401 });
        }

        const userId = `user_${Date.now()}`;
        const userName = email.split("@")[0];

        // Generate proper JWT token
        const token = await signToken({
            sub: userId,
            email,
            name: userName,
        });

        const response = NextResponse.json({
            user: { id: userId, email, name: userName },
            token,
            message: "Login successful",
        });

        // Also set as cookie for SSR
        response.cookies.set("auth_token", token, {
            httpOnly: true,
            secure: true,
            sameSite: "lax",
            maxAge: 60 * 60 * 24 * 7, // 7 days
        });

        console.log("Signin successful for:", email);
        return response;
    } catch (error) {
        console.error("Signin error:", error);
        return NextResponse.json({ message: "Server error" }, { status: 500 });
    }
}

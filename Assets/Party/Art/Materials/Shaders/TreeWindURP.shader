Shader "Alarma/Vegetation/Natural Wind R3"
{
    Properties
    {
        _BaseColor("Color", Color) = (0.4,0.65,0.3,1)
        _WindStrength("Fuerza del viento", Range(0,2)) = 1
        _WindSpeed("Velocidad", Range(0,3)) = 1
        _WindPeriod("Periodo (segundos)", Float) = 8
        _WindDirection("Direccion mundial XZ", Vector) = (0.93,0,0.35,0)
        _PrimaryAmplitude("Balanceo del tronco (m)", Float) = 0.24
        _BranchAmplitude("Balanceo de ramas (m)", Float) = 0.09
        _LeafAmplitude("Aleteo lateral (m)", Float) = 0.045
        _LeafVerticalAmplitude("Aleteo vertical (m)", Float) = 0.028
    }
    SubShader
    {
        Tags { "RenderPipeline"="UniversalPipeline" "RenderType"="Opaque" "Queue"="Geometry" }
        Cull Off
        HLSLINCLUDE
        #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Core.hlsl"
        #include "Packages/com.unity.render-pipelines.universal/ShaderLibrary/Lighting.hlsl"
        #include "Packages/com.unity.render-pipelines.core/ShaderLibrary/Packing.hlsl"
        CBUFFER_START(UnityPerMaterial)
            float4 _BaseColor;
            float4 _WindDirection;
            float _WindStrength, _WindSpeed, _WindPeriod;
            float _PrimaryAmplitude, _BranchAmplitude, _LeafAmplitude, _LeafVerticalAmplitude;
        CBUFFER_END
        struct Attributes
        {
            float4 positionOS : POSITION;
            float3 normalOS : NORMAL;
            float4 windMask : COLOR;
            UNITY_VERTEX_INPUT_INSTANCE_ID
        };
        struct Varyings
        {
            float4 positionCS : SV_POSITION;
            float3 positionWS : TEXCOORD0;
            half3 normalWS : TEXCOORD1;
            half fog : TEXCOORD2;
            UNITY_VERTEX_INPUT_INSTANCE_ID
            UNITY_VERTEX_OUTPUT_STEREO
        };
        // COLOR.a guarda fase, nunca opacidad: las hojas son geometria opaca de doble cara.
        float3 WindPosition(float3 world, float4 mask)
        {
            const float tau = 6.28318530718;
            float time = _Time.y * _WindSpeed * tau / max(_WindPeriod,0.01);
            float spatial = world.x*0.037 + world.z*0.025;
            float gust = 0.65 + 0.35*sin(2*time + spatial*0.37 + 1.2);
            float main = mask.r*_PrimaryAmplitude*sin(time+spatial)*gust;
            float branch = mask.g*_BranchAmplitude*sin(3*time+world.x*0.35+world.z*0.21);
            float phase = mask.a*tau;
            float flutter = mask.b*_LeafAmplitude*sin(9*time+phase+world.x*0.13+world.z*0.11);
            float vertical = mask.b*_LeafVerticalAmplitude*sin(13*time+phase*1.7);
            float2 dir = _WindDirection.xz / max(length(_WindDirection.xz),0.0001);
            float2 side = float2(dir.y,-dir.x);
            float2 lateral = dir*(main+branch)+side*flutter;
            return world+float3(lateral.x,vertical,lateral.y)*_WindStrength;
        }
        Varyings WindVertex(Attributes input)
        {
            Varyings output=(Varyings)0;
            UNITY_SETUP_INSTANCE_ID(input);
            UNITY_TRANSFER_INSTANCE_ID(input,output);
            UNITY_INITIALIZE_VERTEX_OUTPUT_STEREO(output);
            output.positionWS=WindPosition(TransformObjectToWorld(input.positionOS.xyz),input.windMask);
            output.positionCS=TransformWorldToHClip(output.positionWS);
            output.normalWS=TransformObjectToWorldNormal(input.normalOS);
            output.fog=ComputeFogFactor(output.positionCS.z);
            return output;
        }
        half3 DeformedNormal(Varyings input, FRONT_FACE_TYPE facing)
        {
            float3 normal=normalize(cross(ddy(input.positionWS),ddx(input.positionWS)));
            if(dot(normal,input.normalWS)<0)normal=-normal;
            return normal*IS_FRONT_VFACE(facing,1.0,-1.0);
        }
        ENDHLSL
        Pass
        {
            Name "ForwardLit"
            Tags { "LightMode"="UniversalForwardOnly" }
            ZWrite On
            HLSLPROGRAM
            #pragma target 3.5
            #pragma vertex WindVertex
            #pragma fragment ForwardFragment
            #pragma multi_compile_instancing
            #pragma multi_compile_fog
            #pragma multi_compile _ _MAIN_LIGHT_SHADOWS _MAIN_LIGHT_SHADOWS_CASCADE _MAIN_LIGHT_SHADOWS_SCREEN
            #pragma multi_compile_fragment _ _SHADOWS_SOFT _SHADOWS_SOFT_LOW _SHADOWS_SOFT_MEDIUM _SHADOWS_SOFT_HIGH
            #pragma multi_compile _ _ADDITIONAL_LIGHTS
            half4 ForwardFragment(Varyings input, FRONT_FACE_TYPE facing : FRONT_FACE_SEMANTIC) : SV_Target
            {
                UNITY_SETUP_INSTANCE_ID(input);
                UNITY_SETUP_STEREO_EYE_INDEX_POST_VERTEX(input);
                half3 n=DeformedNormal(input,facing);
                Light main=GetMainLight(TransformWorldToShadowCoord(input.positionWS));
                half diffuse=saturate(dot(n,main.direction));
                half transmission=0.14*pow(saturate(dot(-n,main.direction)),2);
                half3 illumination=SampleSH(n)+main.color*(diffuse+transmission)*main.distanceAttenuation*main.shadowAttenuation;
                #if defined(_ADDITIONAL_LIGHTS)
                uint count=GetAdditionalLightsCount();
                for(uint i=0;i<count;++i)
                {
                    Light light=GetAdditionalLight(i,input.positionWS);
                    illumination+=light.color*saturate(dot(n,light.direction))*light.distanceAttenuation*light.shadowAttenuation;
                }
                #endif
                half3 color=MixFog(_BaseColor.rgb*max(illumination,0.06),input.fog);
                return half4(color,1);
            }
            ENDHLSL
        }
        Pass
        {
            Name "ShadowCaster"
            Tags { "LightMode"="ShadowCaster" }
            ZWrite On
            ColorMask 0
            HLSLPROGRAM
            #pragma target 3.5
            #pragma vertex ShadowVertex
            #pragma fragment ShadowFragment
            #pragma multi_compile_instancing
            #pragma multi_compile_vertex _ _CASTING_PUNCTUAL_LIGHT_SHADOW
            float3 _LightDirection, _LightPosition;
            Varyings ShadowVertex(Attributes input)
            {
                Varyings output=WindVertex(input);
                #if defined(_CASTING_PUNCTUAL_LIGHT_SHADOW)
                    float3 lightDirection=normalize(_LightPosition-output.positionWS);
                #else
                    float3 lightDirection=_LightDirection;
                #endif
                output.positionCS=ApplyShadowClamping(TransformWorldToHClip(ApplyShadowBias(output.positionWS,output.normalWS,lightDirection)));
                return output;
            }
            half4 ShadowFragment(Varyings input) : SV_Target { return 0; }
            ENDHLSL
        }
        Pass
        {
            Name "DepthOnly"
            Tags { "LightMode"="DepthOnly" }
            ZWrite On
            ColorMask 0
            HLSLPROGRAM
            #pragma target 3.5
            #pragma vertex WindVertex
            #pragma fragment DepthFragment
            #pragma multi_compile_instancing
            half4 DepthFragment(Varyings input) : SV_Target { return 0; }
            ENDHLSL
        }
        Pass
        {
            Name "DepthNormals"
            Tags { "LightMode"="DepthNormalsOnly" }
            ZWrite On
            HLSLPROGRAM
            #pragma target 3.5
            #pragma vertex WindVertex
            #pragma fragment NormalsFragment
            #pragma multi_compile_instancing
            #pragma multi_compile_fragment _ _GBUFFER_NORMALS_OCT
            half4 NormalsFragment(Varyings input, FRONT_FACE_TYPE facing : FRONT_FACE_SEMANTIC) : SV_Target
            {
                UNITY_SETUP_INSTANCE_ID(input);
                half3 n=DeformedNormal(input,facing);
                #if defined(_GBUFFER_NORMALS_OCT)
                    float2 encoded=saturate(PackNormalOctQuadEncode(n)*0.5+0.5);
                    return half4(PackFloat2To888(encoded),0);
                #else
                    return half4(n,0);
                #endif
            }
            ENDHLSL
        }
    }
    FallBack Off
}

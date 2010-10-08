<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
                xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:template match="/">
        <xsl:for-each select="outline/root/item">
            <xsl:call-template name="item">
                <xsl:with-param name="indent"
                                select="1"/>
                <xsl:with-param name="prefix"
                                select="*"/>
            </xsl:call-template>
        </xsl:for-each>
    </xsl:template>
    <xsl:template name="item">
        <xsl:param name="indent"/>
        <xsl:choose>
            <xsl:when test="$indent = 1">
                <xsl:text>==</xsl:text>
            </xsl:when>
            <xsl:otherwise>
                <xsl:value-of select="$indent"/>
                <xsl:text>- </xsl:text>
            </xsl:otherwise>
        </xsl:choose>
        <xsl:value-of select="values/*[2]/p/run/lit"/>
        <xsl:choose>
            <xsl:when test="$indent = 1">
                <xsl:text>==</xsl:text>
            </xsl:when>
        </xsl:choose>
        <xsl:text>
</xsl:text>
        <xsl:for-each select="children/item">
            <xsl:call-template name="item">
                <xsl:with-param name="indent"
                                select="$indent + 1"/>
            </xsl:call-template>
        </xsl:for-each>
    </xsl:template>
</xsl:stylesheet>
